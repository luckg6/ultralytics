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

优先级从高到低：

1. 不替换全网卷积，只做一个 `FDConvLite`，替换 neck/head 中 1-2 个 3x3 depthwise 卷积。
2. 第一版不做完整 Fourier weight bank，可先做频带门控：低频全局池化 + 高频残差门控。
3. 如果 B-PKI 或 B-FreqFuse 不理想，再考虑 FDConvLite。

## 适合作为哪个实验

- 新 B/C 备选：`B-FDConvLite` 或 `C-FDConvLite`。

## 风险

- 官方 FDConv 目标不是遥感 OBB，迁移动机要写清楚。
- 频域实现容易引入额外计算和数值不稳定，第一版必须轻量。
- 不建议作为下一步首选，优先级低于 PKINet 和 FreqFusion。
