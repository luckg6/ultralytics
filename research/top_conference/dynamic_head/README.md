# Dynamic Head

## 基本信息

- 论文：Dynamic Head: Unifying Object Detection Heads with Attentions
- 会议：CVPR 2021
- 论文链接：https://openaccess.thecvf.com/content/CVPR2021/html/Dai_Dynamic_Head_Unifying_Object_Detection_Heads_With_Attentions_CVPR_2021_paper.html
- PDF：https://openaccess.thecvf.com/content/CVPR2021/papers/Dai_Dynamic_Head_Unifying_Object_Detection_Heads_With_Attentions_CVPR_2021_paper.pdf
- 官方代码：https://github.com/microsoft/DynamicHead

## 可借鉴点

Dynamic Head 从尺度、空间和任务三个维度引入注意力机制。它可以作为检测头增强的备选方向，尤其适合在 DCNv3 实现成本过高时替代创新点 C。

## 迁移到 YOLO11n-OBB 的方案

优先级从高到低：

1. 只借鉴 head attention 思路，在 YOLO OBB head 前加入轻量尺度/空间注意力。
2. 不直接照搬完整 Dynamic Head，避免结构和训练成本过重。
3. 重点观察小目标召回率和 mAP50-95 是否提升。

## 风险

- YOLO 的解耦头结构和 Dynamic Head 原始实现不完全一致，需要改造。
- 注意力模块容易增加延迟。
- 如果 A+B 已经提升明显，C 可以保持为轻量补充，不必强行复杂化。

