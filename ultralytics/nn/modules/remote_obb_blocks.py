"""Custom blocks for remote-sensing small-object OBB experiments."""

from __future__ import annotations

import torch
import torch.nn as nn

from .block import C3k2, SPPF

__all__ = ("C3k2Geo", "DirectionalGeoAttention", "LSKBlock", "SPPFLSK")


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
