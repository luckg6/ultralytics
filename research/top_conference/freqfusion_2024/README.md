# FreqFusion / Frequency-aware Feature Fusion

## 基本信息

- 论文：Frequency-aware Feature Fusion for Dense Image Prediction
- 期刊：TPAMI 2024
- 论文链接：https://arxiv.org/abs/2408.12879
- 官方代码：https://github.com/Linwei-Chen/FreqFusion

## 为什么适合本项目

YOLO 的 neck 依赖上采样和 concat 融合。遥感小目标容易在上采样融合时出现边界模糊和细节丢失，FreqFusion 的动机正好是解决高低分辨率特征融合中的高频细节与类别一致性问题。A-P2 的强提升说明更高分辨率特征对 DIOR-R 小目标重要，因此在 A 之后尝试更聪明的 feature fusion 很自然。

## 可迁移方案

第四章已实现轻量 `FreqDetailFusion`，替换原 top-down P5->P4、P4->P3 两次融合入口，保留 OBB Head 和三尺度预测。该实现借鉴频率细节与融合一致性动机，不完整迁移官方 ALPF/AHPF/offset resampling。

## 适合作为哪个实验

- 第四章 D 候选：`FDF`。OAC+FDF、Blend 和 FDConv-Lite+FDF 均未达到最终要求；当前暂保留 FDF，与 SGC 重新测试互补性。

## 风险

- 原始 FreqFusion 代码面向 dense prediction，部分实现基于 mmseg/mmdet 思路。
- 完整模块可能偏重，第一版只做最轻量的频率门控融合。
- 如果只提升分割边界而不提升 OBB mAP，需要及时停止。
