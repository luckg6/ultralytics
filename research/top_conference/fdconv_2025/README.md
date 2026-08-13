# FDConv / Frequency Dynamic Convolution

## 基本信息

- 论文：Frequency Dynamic Convolution for Dense Image Prediction
- 会议：CVPR 2025
- 论文链接：https://arxiv.org/abs/2503.18783
- PDF：https://openaccess.thecvf.com/content/CVPR2025/papers/Chen_Frequency_Dynamic_Convolution_for_Dense_Image_Prediction_CVPR_2025_paper.pdf
- 官方代码：https://github.com/Linwei-Chen/FDConv

## 为什么适合本项目

FDConv 从频域构造动态卷积权重，目标是用较少参数获得更丰富的动态卷积表达。遥感影像中目标和背景纹理复杂，频域动态卷积可能比普通注意力更适合区分小目标细节和背景纹理。

## 可迁移方案

已实现过 `FDConvLiteAdapter`：不替换全网卷积，而是在第四章 LSKNet-T 的 P3/P4/P5 通道适配后做频域统计路由和多尺度 depthwise 动态校准。它是 FDConv 启发的轻量迁移，不声称复现官方完整 Fourier weight bank。

## 适合作为哪个实验

- 第四章历史 C-v2 候选：`FDConv-Lite`；组合候选为 `FDConv-Lite + FDF`。DIOR-R seed 42 筛选中，组合低于单 FDF 与单 FDConv-Lite，因此不继续扩展三 seed。

## 风险

- 官方 FDConv 目标不是遥感 OBB，迁移动机要写清楚。
- 频域实现容易引入额外计算和数值不稳定，第一版必须轻量。
- seed 42 和后续多 seed 结果尚未产生，因此目前只能称候选，不能写成定稿创新。

实现与命令见 `experiments/chapter4/README.md`。
