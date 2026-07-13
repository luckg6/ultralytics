"""Custom blocks for remote-sensing small-object OBB experiments."""

from __future__ import annotations

import torch
import torch.nn as nn

from .block import C3k2, SPPF

__all__ = (
    "C3k2Geo",
    "C3k2GeoPlus",
    "C3k2PKI",
    "DirectionalGeoAttention",
    "DirectionalGeoPlusAttention",
    "LSKBlock",
    "PKIContext",
    "SPPFLSK",
)


class ConvBNAct(nn.Module):
    """Small local Conv-BN-SiLU helper used by remote OBB experimental blocks."""

    def __init__(self, c1: int, c2: int, k=1, s=1, p=None, g: int = 1):
        """Initialize a convolution block with automatic same padding."""
        super().__init__()
        if p is None:
            if isinstance(k, tuple):
                p = tuple(v // 2 for v in k)
            else:
                p = k // 2
        self.conv = nn.Conv2d(c1, c2, k, s, p, groups=g, bias=False)
        self.bn = nn.BatchNorm2d(c2)
        self.act = nn.SiLU(inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply convolution, normalization, and activation."""
        return self.act(self.bn(self.conv(x)))


class PKIContext(nn.Module):
    """Lightweight Poly-Kernel Inception context block for remote-sensing neck fusion.

    This block borrows the PKINet idea of combining multiple depthwise kernel
    scopes with context anchor attention, but keeps the implementation small and
    dependency-free for YOLO11n-OBB ablations.
    """

    def __init__(self, c1: int, expansion: float = 0.5, caa_kernel: int = 11):
        """Initialize a lightweight PKI-style context module."""
        super().__init__()
        c_mid = max(int(c1 * expansion), 16)
        self.reduce = ConvBNAct(c1, c_mid, 1, p=0)
        self.dw3 = nn.Conv2d(c_mid, c_mid, 3, padding=1, groups=c_mid, bias=False)
        self.dw5 = nn.Conv2d(c_mid, c_mid, 5, padding=2, groups=c_mid, bias=False)
        self.dw7 = nn.Conv2d(c_mid, c_mid, 7, padding=6, dilation=2, groups=c_mid, bias=False)
        self.mix_bn = nn.BatchNorm2d(c_mid)
        self.mix_act = nn.SiLU(inplace=True)

        pad = caa_kernel // 2
        self.caa = nn.Sequential(
            nn.AvgPool2d(7, stride=1, padding=3),
            ConvBNAct(c_mid, c_mid, 1, p=0),
            nn.Conv2d(c_mid, c_mid, (1, caa_kernel), padding=(0, pad), groups=c_mid, bias=False),
            nn.Conv2d(c_mid, c_mid, (caa_kernel, 1), padding=(pad, 0), groups=c_mid, bias=False),
            nn.BatchNorm2d(c_mid),
            nn.SiLU(inplace=True),
            nn.Conv2d(c_mid, c_mid, 1, bias=True),
            nn.Sigmoid(),
        )
        self.restore = ConvBNAct(c_mid, c1, 1, p=0)
        self.gamma = nn.Parameter(torch.zeros(1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply poly-kernel context modulation with a stable residual gate."""
        y = self.reduce(x)
        multi_kernel = self.dw3(y) + self.dw5(y) + self.dw7(y)
        multi_kernel = self.mix_act(self.mix_bn(multi_kernel))
        context = multi_kernel * self.caa(y)
        return x + self.gamma * self.restore(context)


class LSKBlock(nn.Module):
    """Lightweight large-selective-kernel attention for remote-sensing context modeling.

    The block keeps the input and output channels unchanged, making it safe to
    insert into an existing YOLO feature stage. It follows the LSKNet idea of
    selecting between local and larger-context depthwise branches, but uses only
    standard PyTorch layers and a zero-initialized residual scale for stable
    training from YOLO pretrained weights.
    """

    def __init__(self, c1: int):
        """Initialize the LSK-style block.

        Args:
            c1 (int): Number of input and output channels.
        """
        super().__init__()
        c_mid = max(c1 // 2, 16)
        self.conv_local = nn.Conv2d(c1, c1, 5, padding=2, groups=c1, bias=True)
        self.conv_context = nn.Conv2d(c1, c1, 7, padding=9, dilation=3, groups=c1, bias=True)
        self.reduce_local = nn.Conv2d(c1, c_mid, 1, bias=True)
        self.reduce_context = nn.Conv2d(c1, c_mid, 1, bias=True)
        self.select = nn.Conv2d(2, 2, 7, padding=3, bias=True)
        self.restore = nn.Conv2d(c_mid, c1, 1, bias=True)
        self.gamma = nn.Parameter(torch.zeros(1))
        self.act = nn.Sigmoid()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply selective local/context spatial attention."""
        local = self.conv_local(x)
        context = self.conv_context(local)
        local = self.reduce_local(local)
        context = self.reduce_context(context)
        features = torch.cat((local, context), dim=1)

        pooled = torch.cat(
            (
                torch.mean(features, dim=1, keepdim=True),
                torch.max(features, dim=1, keepdim=True)[0],
            ),
            dim=1,
        )
        weights = self.act(self.select(pooled))
        attention = local * weights[:, 0:1] + context * weights[:, 1:2]
        attention = self.act(self.restore(attention))
        return x + self.gamma * x * attention


class SPPFLSK(SPPF):
    """SPPF followed by an LSK-style context block while preserving SPPF weight names."""

    def __init__(self, c1: int, c2: int, k: int = 5):
        """Initialize SPPF with a lightweight context attention block."""
        super().__init__(c1, c2, k)
        self.lsk = LSKBlock(c2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply SPPF and then LSK-style context attention."""
        return self.lsk(super().forward(x))


class C3k2PKI(C3k2):
    """C3k2 followed by a lightweight PKINet-style context block for neck fusion."""

    def __init__(
        self,
        c1: int,
        c2: int,
        n: int = 1,
        c3k: bool = False,
        e: float = 0.5,
        attn: bool = False,
        g: int = 1,
        shortcut: bool = True,
    ):
        """Initialize C3k2 and append a PKI-style multi-kernel context block."""
        super().__init__(c1, c2, n, c3k, e, attn, g, shortcut)
        self.pki = PKIContext(c2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply C3k2 followed by lightweight poly-kernel context modulation."""
        return self.pki(super().forward(x))


class DirectionalGeoAttention(nn.Module):
    """Lightweight directional attention for rotated-object geometric adaptation."""

    def __init__(self, c1: int, reduction: int = 16, k: int = 7):
        """Initialize horizontal, vertical, and dilated directional branches."""
        super().__init__()
        c_mid = max(c1 // reduction, 16)
        pad = k // 2
        self.dw_h = nn.Conv2d(c1, c1, (1, k), padding=(0, pad), groups=c1, bias=True)
        self.dw_v = nn.Conv2d(c1, c1, (k, 1), padding=(pad, 0), groups=c1, bias=True)
        self.dw_d = nn.Conv2d(c1, c1, 3, padding=2, dilation=2, groups=c1, bias=True)
        self.selector = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(c1, c_mid, 1, bias=True),
            nn.SiLU(),
            nn.Conv2d(c_mid, 3, 1, bias=True),
        )
        self.spatial = nn.Conv2d(2, 1, 7, padding=3, bias=True)
        self.act = nn.Sigmoid()
        self.softmax = nn.Softmax(dim=1)
        self.gamma = nn.Parameter(torch.tensor(0.1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply input-adaptive directional modulation."""
        h = self.dw_h(x)
        v = self.dw_v(x)
        d = self.dw_d(x)
        weights = self.softmax(self.selector(x))
        oriented = h * weights[:, 0:1] + v * weights[:, 1:2] + d * weights[:, 2:3]
        pooled = torch.cat((torch.mean(oriented, dim=1, keepdim=True), torch.max(oriented, dim=1, keepdim=True)[0]), dim=1)
        gate = self.act(self.spatial(pooled))
        return x + self.gamma * oriented * gate


class DirectionalGeoPlusAttention(nn.Module):
    """Stronger directional geometry block for C-Dynamic-Plus head features."""

    def __init__(self, c1: int, expansion: float = 0.125, k: int = 7, max_mid: int = 96):
        """Initialize a moderately heavier orientation-aware modulation block."""
        super().__init__()
        c_mid = max(min(int(c1 * expansion), max_mid), 32)
        c_gate = max(c_mid // 4, 16)
        pad = k // 2
        self.reduce = ConvBNAct(c1, c_mid, 1, p=0)
        self.dw_h = nn.Conv2d(c_mid, c_mid, (1, k), padding=(0, pad), groups=c_mid, bias=False)
        self.dw_v = nn.Conv2d(c_mid, c_mid, (k, 1), padding=(pad, 0), groups=c_mid, bias=False)
        self.dw_d = nn.Conv2d(c_mid, c_mid, 3, padding=2, dilation=2, groups=c_mid, bias=False)
        self.dw_x = nn.Sequential(
            nn.Conv2d(c_mid, c_mid, (1, k), padding=(0, pad), groups=c_mid, bias=False),
            nn.Conv2d(c_mid, c_mid, (k, 1), padding=(pad, 0), groups=c_mid, bias=False),
        )
        self.branch_bn = nn.BatchNorm2d(c_mid)
        self.branch_act = nn.SiLU(inplace=True)
        self.selector = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(c_mid, c_gate, 1, bias=True),
            nn.SiLU(inplace=True),
            nn.Conv2d(c_gate, 4, 1, bias=True),
        )
        self.channel_gate = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(c_mid, c_gate, 1, bias=True),
            nn.SiLU(inplace=True),
            nn.Conv2d(c_gate, c_mid, 1, bias=True),
            nn.Sigmoid(),
        )
        self.spatial_gate = nn.Sequential(nn.Conv2d(2, 1, 7, padding=3, bias=True), nn.Sigmoid())
        self.restore = ConvBNAct(c_mid, c1, 1, p=0)
        self.softmax = nn.Softmax(dim=1)
        self.gamma = nn.Parameter(torch.tensor(0.1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply orientation-selective spatial and channel modulation."""
        y = self.reduce(x)
        branches = torch.stack((self.dw_h(y), self.dw_v(y), self.dw_d(y), self.dw_x(y)), dim=1)
        weights = self.softmax(self.selector(y)).unsqueeze(2)
        oriented = (branches * weights).sum(dim=1)
        oriented = self.branch_act(self.branch_bn(oriented))
        pooled = torch.cat((torch.mean(oriented, dim=1, keepdim=True), torch.max(oriented, dim=1, keepdim=True)[0]), dim=1)
        modulated = oriented * self.spatial_gate(pooled) * self.channel_gate(oriented)
        return x + self.gamma * self.restore(modulated)


class C3k2Geo(C3k2):
    """C3k2 with lightweight directional geometry attention for OBB head features."""

    def __init__(
        self,
        c1: int,
        c2: int,
        n: int = 1,
        c3k: bool = False,
        e: float = 0.5,
        attn: bool = False,
        g: int = 1,
        shortcut: bool = True,
    ):
        """Initialize C3k2 and append a directional geometry attention block."""
        super().__init__(c1, c2, n, c3k, e, attn, g, shortcut)
        self.geo = DirectionalGeoAttention(c2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply C3k2 followed by directional geometry attention."""
        return self.geo(super().forward(x))


class C3k2GeoPlus(C3k2):
    """C3k2 with stronger directional geometry attention for C-Dynamic-Plus."""

    def __init__(
        self,
        c1: int,
        c2: int,
        n: int = 1,
        c3k: bool = False,
        e: float = 0.5,
        attn: bool = False,
        g: int = 1,
        shortcut: bool = True,
    ):
        """Initialize C3k2 and append the stronger geometry attention block."""
        super().__init__(c1, c2, n, c3k, e, attn, g, shortcut)
        self.geo = DirectionalGeoPlusAttention(c2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply C3k2 followed by C-Dynamic-Plus geometry attention."""
        return self.geo(super().forward(x))
