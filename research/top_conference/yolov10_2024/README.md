# YOLOv10

## 基本信息

- 论文：YOLOv10: Real-Time End-to-End Object Detection
- 会议：NeurIPS 2024
- 论文链接：https://arxiv.org/abs/2405.14458
- 官方代码：https://github.com/THU-MIG/yolov10

## 为什么放进候选

YOLOv10 不是遥感 OBB 论文，也不直接解决小目标旋转框问题，但它对 YOLO 系列的效率、冗余结构和训练分配做了系统优化。当前项目已经基于 YOLO11n-OBB，YOLOv10 更适合作为效率和训练策略参考，而不是直接作为结构创新点。

## 可迁移方案

优先级从高到低：

1. 只参考轻量化设计和训练分配思想，不切换主模型。
2. 如果后续需要部署指标，可借鉴其效率分析方式，补充 Params、GFLOPs、FPS。
3. 不建议当前阶段引入 NMS-free OBB 训练，改动过大。

## 适合作为哪个实验

- 不建议作为 A/B/C 主实验。
- 可作为论文方法讨论或部署效率参考。

## 风险

- 与 Ultralytics YOLO11n-OBB 的结构和训练逻辑不同。
- NMS-free 思路迁移到 OBB 后处理成本高。
- 当前论文主线应优先保持结构消融清晰。
