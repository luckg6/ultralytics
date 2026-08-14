# Strip R-CNN / Large Strip Convolution

更新日期：2026-08-13

## 来源

- 论文：`Strip R-CNN: Large Strip Convolution for Remote Sensing Object Detection`
- 版本：arXiv 2025；AAAI 2026 official implementation
- 论文页：https://arxiv.org/abs/2501.03775
- 官方代码：https://github.com/HVision-NKU/Strip-R-CNN

## 核心思想

Strip R-CNN 针对遥感目标检测中的高长宽比目标和复杂方向变化，提出使用 sequential orthogonal large strip convolutions，而不是只用方形大核或全局注意力做均匀上下文聚合。论文同时提出在定位分支中使用 strip convolutions 以增强旋转目标定位能力。

## 与第四章的关系

第四章当前 LSKNet-T baseline 已经具备遥感专用大选择核 backbone，但小目标和方向/几何定位仍有提升空间。FDConv-Lite 说明频域动态适配与 FDF 容易形成重叠，组合没有带来互补。因此下一轮 C 候选应转向空间几何和形状建模。

推荐迁移为轻量 `SGC` / `Strip-Guided Calibration`：

```text
LSKNet-T C3/C4/C5 output
-> 1x1 channel adapter
-> SGC on P3/P4/P5
-> original YOLO11 Neck or FDF-enhanced top-down neck
-> original YOLO11 OBB Head
```

设计原则：

- 不整体替换 LSKNet-T backbone，不使用 StripNet backbone checkpoint，避免把 baseline 变成另一个 backbone；
- 不复制第三章 FSPB 的 P2 分支，也不复制 LPCF 的 poly-kernel context fusion；
- 不整体堆叠频域模块；若后续仍借鉴 FDF，需要改成更温和的残差/单尺度方式，避免与 SGC 负交互；
- 使用标准 PyTorch depthwise strip convolution，例如 `1xk`、`kx1`、`1xk + kx1` 或小残差门控；
- 首轮 seed 42 已完成：`SGC` 单模块成立，直接 `SGC+FDF` 低于两个单模块，因此停止扩展该直接组合。

## 风险

- Strip R-CNN 官方实现基于 MMRotate，不能直接整体并入当前 Ultralytics 项目；
- 官方源码 2026-08-13 直连 GitHub 克隆超时，当前只完成论文/README 层面的核验；
- LSKNet 本身已有大核选择机制，论文叙事必须强调 `SGC` 是方向性条带几何校准，而不是重复 LSKNet 的大范围上下文选择。

## 已核实源码要点

用户已手动解压官方仓库到 `research/external_repos/Strip-R-CNN/`，已核实以下文件存在：

- `README.md`
- `configs/strip_rcnn/strip_rcnn_s_fpn_1x_dior_le90.py`
- `mmrotate/models/backbones/stripnet.py`
- `mmrotate/models/roi_heads/bbox_heads/strip_head.py`

`stripnet.py` 中的 `StripBlock` 结构为：

```text
x
-> DWConv 5x5
-> DWConv 1x19
-> DWConv 19x1
-> Conv 1x1
-> x * attn
```

`Attention` 外层还有 `1x1 projection -> GELU -> StripBlock -> 1x1 projection -> residual`。官方 DIOR 配置使用 `StripNet-S`，`embed_dims=[64,128,320,512]`，`k2s=[19,19,19,19]`，检测框架是两阶段 Strip R-CNN。第四章不应整体搬运 StripNet backbone 或两阶段 ROI head，只迁移条带几何校准思想。

## 当前建议

作为下一轮 C 候选优先级最高。若源码后续补齐，只用来核对 strip module 的结构细节；当前轻量实现可以不依赖官方仓库，直接用标准 PyTorch 实现。
