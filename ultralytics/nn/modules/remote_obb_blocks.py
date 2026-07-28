"""Custom blocks for remote-sensing small-object OBB experiments."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .block import C3k2, SPPF

__all__ = (
    "C3k2Geo",
    "C3k2GeoPlus",
    "C3k2GRA",
    "C3k2P2Guard",
    "C3k2PKI",
    "DirectionalGeoAttention",
    "DirectionalGeoPlusAttention",
    "GRALiteAttention",
    "LSKBlock",
    "LSKNetT",
    "PKIContext",
    "P2SemanticGuard",
    "ResidualFeatureBlend",
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


class DropPath(nn.Module):
    """Stochastic depth used by the official LSKNet blocks."""

    def __init__(self, drop_prob: float = 0.0):
        """Initialize stochastic depth with a per-sample drop probability."""
        super().__init__()
        self.drop_prob = float(drop_prob)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply stochastic depth during training and identity during evaluation."""
        if self.drop_prob == 0.0 or not self.training:
            return x
        keep_prob = 1.0 - self.drop_prob
        shape = (x.shape[0],) + (1,) * (x.ndim - 1)
        random_tensor = keep_prob + torch.rand(shape, dtype=x.dtype, device=x.device)
        return x.div(keep_prob) * random_tensor.floor()


class LSKNetDWConv(nn.Module):
    """Depthwise convolution inside the LSKNet MLP block."""

    def __init__(self, dim: int):
        """Initialize a 3x3 depthwise convolution."""
        super().__init__()
        self.dwconv = nn.Conv2d(dim, dim, 3, 1, 1, bias=True, groups=dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply depthwise convolution."""
        return self.dwconv(x)


class LSKNetMlp(nn.Module):
    """Convolutional MLP used by LSKNet."""

    def __init__(self, in_features: int, hidden_features: int | None = None, out_features: int | None = None, drop: float = 0.0):
        """Initialize pointwise-depthwise-pointwise MLP."""
        super().__init__()
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        self.fc1 = nn.Conv2d(in_features, hidden_features, 1)
        self.dwconv = LSKNetDWConv(hidden_features)
        self.act = nn.GELU()
        self.fc2 = nn.Conv2d(hidden_features, out_features, 1)
        self.drop = nn.Dropout(drop)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply the LSKNet MLP."""
        x = self.fc1(x)
        x = self.dwconv(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        return self.drop(x)


class LSKNetSelectiveKernel(nn.Module):
    """Official LSKNet selective large-kernel attention block."""

    def __init__(self, dim: int):
        """Initialize local and dilated spatial branches."""
        super().__init__()
        self.conv0 = nn.Conv2d(dim, dim, 5, padding=2, groups=dim)
        self.conv_spatial = nn.Conv2d(dim, dim, 7, stride=1, padding=9, groups=dim, dilation=3)
        self.conv1 = nn.Conv2d(dim, dim // 2, 1)
        self.conv2 = nn.Conv2d(dim, dim // 2, 1)
        self.conv_squeeze = nn.Conv2d(2, 2, 7, padding=3)
        self.conv = nn.Conv2d(dim // 2, dim, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Select between local and large-context depthwise branches."""
        attn1 = self.conv0(x)
        attn2 = self.conv_spatial(attn1)
        attn1 = self.conv1(attn1)
        attn2 = self.conv2(attn2)

        attn = torch.cat([attn1, attn2], dim=1)
        avg_attn = torch.mean(attn, dim=1, keepdim=True)
        max_attn = torch.max(attn, dim=1, keepdim=True)[0]
        sig = self.conv_squeeze(torch.cat([avg_attn, max_attn], dim=1)).sigmoid()
        attn = attn1 * sig[:, 0:1] + attn2 * sig[:, 1:2]
        return x * self.conv(attn)


class LSKNetAttention(nn.Module):
    """Attention wrapper used in each LSKNet block."""

    def __init__(self, d_model: int):
        """Initialize projection, selective-kernel gating, and output projection."""
        super().__init__()
        self.proj_1 = nn.Conv2d(d_model, d_model, 1)
        self.activation = nn.GELU()
        self.spatial_gating_unit = LSKNetSelectiveKernel(d_model)
        self.proj_2 = nn.Conv2d(d_model, d_model, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply LSK attention with a residual connection."""
        shortcut = x
        x = self.proj_1(x)
        x = self.activation(x)
        x = self.spatial_gating_unit(x)
        x = self.proj_2(x)
        return x + shortcut


class LSKNetStageBlock(nn.Module):
    """One official LSKNet residual block."""

    def __init__(self, dim: int, mlp_ratio: float = 4.0, drop: float = 0.0, drop_path: float = 0.0):
        """Initialize normalization, attention, MLP, layer scales, and drop path."""
        super().__init__()
        self.norm1 = nn.BatchNorm2d(dim)
        self.norm2 = nn.BatchNorm2d(dim)
        self.attn = LSKNetAttention(dim)
        self.drop_path = DropPath(drop_path) if drop_path > 0.0 else nn.Identity()
        self.mlp = LSKNetMlp(in_features=dim, hidden_features=int(dim * mlp_ratio), drop=drop)
        self.layer_scale_1 = nn.Parameter(1e-2 * torch.ones(dim), requires_grad=True)
        self.layer_scale_2 = nn.Parameter(1e-2 * torch.ones(dim), requires_grad=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply attention and MLP residual updates."""
        scale1 = self.layer_scale_1.view(1, -1, 1, 1)
        scale2 = self.layer_scale_2.view(1, -1, 1, 1)
        x = x + self.drop_path(scale1 * self.attn(self.norm1(x)))
        return x + self.drop_path(scale2 * self.mlp(self.norm2(x)))


class LSKNetOverlapPatchEmbed(nn.Module):
    """Overlapping patch embedding used by LSKNet."""

    def __init__(self, patch_size: int, stride: int, in_chans: int, embed_dim: int):
        """Initialize convolutional patch embedding and batch normalization."""
        super().__init__()
        self.proj = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=stride, padding=patch_size // 2)
        self.norm = nn.BatchNorm2d(embed_dim)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, int, int]:
        """Project image/features to a stage feature map."""
        x = self.proj(x)
        _, _, h, w = x.shape
        return self.norm(x), h, w


class LSKNetT(nn.Module):
    """Dependency-free LSKNet-T backbone adapted for Ultralytics YAML parsing.

    It follows the official LSKNet-T setting used by the DOTA Oriented R-CNN
    checkpoint: embed_dims=[32, 64, 160, 256] and depths=[3, 3, 5, 2].
    The attribute names mirror the official implementation so that checkpoint
    keys can be loaded after stripping the ``backbone.`` prefix.
    """

    def __init__(
        self,
        in_chans: int = 3,
        embed_dims: list[int] | None = None,
        depths: list[int] | None = None,
        mlp_ratios: list[float] | None = None,
        drop_rate: float = 0.1,
        drop_path_rate: float = 0.1,
    ):
        """Initialize LSKNet-T stages."""
        super().__init__()
        embed_dims = embed_dims or [32, 64, 160, 256]
        depths = depths or [3, 3, 5, 2]
        mlp_ratios = mlp_ratios or [8, 8, 4, 4]
        self.embed_dims = embed_dims
        self.depths = depths
        self.num_stages = len(embed_dims)

        dpr = torch.linspace(0, drop_path_rate, sum(depths)).tolist()
        cur = 0
        for i in range(self.num_stages):
            patch_embed = LSKNetOverlapPatchEmbed(
                patch_size=7 if i == 0 else 3,
                stride=4 if i == 0 else 2,
                in_chans=in_chans if i == 0 else embed_dims[i - 1],
                embed_dim=embed_dims[i],
            )
            block = nn.ModuleList(
                LSKNetStageBlock(embed_dims[i], mlp_ratios[i], drop_rate, dpr[cur + j]) for j in range(depths[i])
            )
            norm = nn.LayerNorm(embed_dims[i])
            cur += depths[i]
            setattr(self, f"patch_embed{i + 1}", patch_embed)
            setattr(self, f"block{i + 1}", block)
            setattr(self, f"norm{i + 1}", norm)

    def forward(self, x: torch.Tensor) -> list[torch.Tensor]:
        """Return C2, C3, C4, and C5 features at strides 4, 8, 16, and 32."""
        b = x.shape[0]
        outs = []
        for i in range(self.num_stages):
            patch_embed = getattr(self, f"patch_embed{i + 1}")
            block = getattr(self, f"block{i + 1}")
            norm = getattr(self, f"norm{i + 1}")
            x, h, w = patch_embed(x)
            for blk in block:
                x = blk(x)
            x = x.flatten(2).transpose(1, 2)
            x = norm(x)
            x = x.reshape(b, h, w, -1).permute(0, 3, 1, 2).contiguous()
            outs.append(x)
        return outs


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


class P2SemanticGuard(nn.Module):
    """Suppress texture-driven P2 responses with low-frequency semantic context."""

    def __init__(self, c1: int, expansion: float = 1.0, context_kernel: int = 11):
        """Initialize local-detail, semantic-context, channel, and spatial gates."""
        super().__init__()
        c_mid = max(int(c1 * expansion), 32)
        c_gate = max(c_mid // 4, 16)
        pad = context_kernel // 2

        self.reduce = ConvBNAct(c1, c_mid, 1, p=0)
        self.local = nn.Sequential(
            nn.Conv2d(c_mid, c_mid, 3, padding=1, groups=c_mid, bias=False),
            nn.BatchNorm2d(c_mid),
            nn.SiLU(inplace=True),
        )
        self.semantic = nn.Sequential(
            nn.AvgPool2d(7, stride=1, padding=3),
            nn.Conv2d(c_mid, c_mid, (1, context_kernel), padding=(0, pad), groups=c_mid, bias=False),
            nn.Conv2d(c_mid, c_mid, (context_kernel, 1), padding=(pad, 0), groups=c_mid, bias=False),
            nn.BatchNorm2d(c_mid),
            nn.SiLU(inplace=True),
        )
        self.channel_gate = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(c_mid, c_gate, 1, bias=True),
            nn.SiLU(inplace=True),
            nn.Conv2d(c_gate, c_mid, 1, bias=True),
            nn.Sigmoid(),
        )
        self.spatial_gate = nn.Sequential(
            nn.Conv2d(2, 1, 7, padding=3, bias=True),
            nn.Sigmoid(),
        )
        self.restore = ConvBNAct(c_mid, c1, 1, p=0)
        self.refine_scale = nn.Parameter(torch.zeros(1))
        self.suppress_scale = nn.Parameter(torch.zeros(1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Refine P2 details and learn to attenuate unsupported spatial responses."""
        y = self.reduce(x)
        context = self.local(y) + self.semantic(y)
        channel = self.channel_gate(context)
        spatial = self.spatial_gate(
            torch.cat((context.mean(dim=1, keepdim=True), context.amax(dim=1, keepdim=True)), dim=1)
        )
        refined = self.restore(context * channel * spatial)
        suppress = 2.0 * spatial - 1.0
        return x * (1.0 + torch.tanh(self.suppress_scale) * suppress) + torch.tanh(self.refine_scale) * refined


class C3k2P2Guard(C3k2):
    """A strengthened C3k2 P2 fusion block with semantic false-positive suppression."""

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
        """Initialize the base fusion block and its P2-specific semantic guard."""
        super().__init__(c1, c2, n, c3k, e, attn, g, shortcut)
        self.guard = P2SemanticGuard(c2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Fuse top-down and backbone P2 features, then suppress unsupported details."""
        return self.guard(super().forward(x))


class ResidualFeatureBlend(nn.Module):
    """Inject an auxiliary feature path through a zero-initialized channel-wise residual gate."""

    def __init__(self, c1: int):
        """Initialize an identity-preserving blend for two equal-channel feature maps."""
        super().__init__()
        self.alpha = nn.Parameter(torch.zeros(1, c1, 1, 1))

    def forward(self, features: list[torch.Tensor]) -> torch.Tensor:
        """Blend the main and auxiliary paths while starting exactly from the main path."""
        main, auxiliary = features
        if main.shape != auxiliary.shape:
            raise ValueError(f"ResidualFeatureBlend requires matching shapes, got {main.shape} and {auxiliary.shape}")
        return main + torch.tanh(self.alpha) * (auxiliary - main)


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


class MaskedDirectionalDWConv(nn.Module):
    """Depthwise convolution constrained to one fixed orientation mask."""

    def __init__(self, c1: int, mask: torch.Tensor):
        """Initialize a masked 7x7 depthwise convolution."""
        super().__init__()
        k = int(mask.shape[-1])
        self.weight = nn.Parameter(torch.empty(c1, 1, k, k))
        self.bias = nn.Parameter(torch.zeros(c1))
        self.register_buffer("mask", mask.view(1, 1, k, k))
        nn.init.kaiming_normal_(self.weight, mode="fan_out", nonlinearity="relu")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply masked depthwise convolution."""
        k = self.weight.shape[-1]
        return F.conv2d(x, self.weight * self.mask, self.bias, padding=k // 2, groups=x.shape[1])


def _orientation_masks(k: int = 7) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Create horizontal, vertical, and two diagonal line masks."""
    masks = []
    center = k // 2
    for orientation in range(4):
        mask = torch.zeros(k, k)
        for i in range(k):
            if orientation == 0:
                mask[center, i] = 1.0
            elif orientation == 1:
                mask[i, center] = 1.0
            elif orientation == 2:
                mask[i, i] = 1.0
            else:
                mask[i, k - 1 - i] = 1.0
        masks.append(mask)
    return tuple(masks)


class GRALiteAttention(nn.Module):
    """Lightweight GRA-style orientation routing for OBB head features.

    The block adapts GRA's group-wise rotating and attention idea with fixed
    orientation-masked depthwise kernels, avoiding MMDetection/MMCV and custom
    rotated convolution dependencies.
    """

    def __init__(self, c1: int, expansion: float = 0.125, k: int = 7, max_mid: int = 96):
        """Initialize orientation-masked branches and input-adaptive routing."""
        super().__init__()
        c_mid = max(min(int(c1 * expansion), max_mid), 32)
        c_gate = max(c_mid // 4, 16)
        self.reduce = ConvBNAct(c1, c_mid, 1, p=0)
        self.branches = nn.ModuleList(MaskedDirectionalDWConv(c_mid, mask) for mask in _orientation_masks(k))
        self.branch_bn = nn.BatchNorm2d(c_mid)
        self.branch_act = nn.SiLU(inplace=True)
        self.routing = nn.Sequential(
            nn.Conv2d(c_mid, c_mid, 3, padding=1, groups=c_mid, bias=False),
            nn.BatchNorm2d(c_mid),
            nn.SiLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(c_mid, c_gate, 1, bias=True),
            nn.SiLU(inplace=True),
            nn.Conv2d(c_gate, 4, 1, bias=True),
        )
        self.group_gate = nn.Sequential(
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
        """Route features through orientation-aware masked depthwise branches."""
        y = self.reduce(x)
        branches = torch.stack([branch(y) for branch in self.branches], dim=1)
        weights = self.softmax(self.routing(y)).unsqueeze(2)
        oriented = (branches * weights).sum(dim=1)
        oriented = self.branch_act(self.branch_bn(oriented))
        pooled = torch.cat((torch.mean(oriented, dim=1, keepdim=True), torch.max(oriented, dim=1, keepdim=True)[0]), dim=1)
        modulated = oriented * self.group_gate(oriented) * self.spatial_gate(pooled)
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


class C3k2GRA(C3k2):
    """C3k2 with lightweight GRA-style orientation routing for OBB head features."""

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
        """Initialize C3k2 and append the GRA-Lite orientation block."""
        super().__init__(c1, c2, n, c3k, e, attn, g, shortcut)
        self.gra = GRALiteAttention(c2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Apply C3k2 followed by lightweight GRA-style orientation routing."""
        return self.gra(super().forward(x))
