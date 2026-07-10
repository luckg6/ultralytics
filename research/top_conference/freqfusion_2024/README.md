# FreqFusion / Frequency-aware Feature Fusion

## 基本信息

- 论文：Frequency-aware Feature Fusion for Dense Image Prediction
- 期刊：TPAMI 2024
- 论文链接：https://arxiv.org/abs/2408.12879
- 官方代码：https://github.com/Linwei-Chen/FreqFusion

## 为什么适合本项目

YOLO 的 neck 依赖上采样和 concat 融合。遥感小目标容易在上采样融合时出现边界模糊和细节丢失，FreqFusion 的动机正好是解决高低分辨率特征融合中的高频细节与类别一致性问题。A-P2 的强提升说明更高分辨率特征对 DIOR-R 小目标重要，因此在 A 之后尝试更聪明的 feature fusion 很自然。

## 可迁移方案

优先级从高到低：

1. 做 `FreqFuseLite`，替换 neck 中 P4->P3 或 P3->P2 的一次上采样融合。
2. 只保留高通增强和轻量低通门控，不引入 offset resampling，避免复杂依赖。
3. 若 `A+C` 有效，再尝试 `A+FreqFuseLite`，观察小目标 mAP50-95 是否继续上升。

## 适合作为哪个实验

- 新 B 候选：`B-FreqFuse`。
- 也可作为 A 的增强版：`A-FreqP2`，但论文消融时要和 A-P2 区分。

## 风险

- 原始 FreqFusion 代码面向 dense prediction，部分实现基于 mmseg/mmdet 思路。
- 完整模块可能偏重，第一版只做最轻量的频率门控融合。
- 如果只提升分割边界而不提升 OBB mAP，需要及时停止。
