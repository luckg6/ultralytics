# EfficientDet / BiFPN

## 基本信息

- 论文：EfficientDet: Scalable and Efficient Object Detection
- 会议：CVPR 2020
- 论文链接：https://openaccess.thecvf.com/content_CVPR_2020/html/Tan_EfficientDet_Scalable_and_Efficient_Object_Detection_CVPR_2020_paper.html
- PDF：https://openaccess.thecvf.com/content_CVPR_2020/papers/Tan_EfficientDet_Scalable_and_Efficient_Object_Detection_CVPR_2020_paper.pdf
- 官方/常用代码入口：https://github.com/google/automl/tree/master/efficientdet

## 可借鉴点

BiFPN 的核心价值是加权双向多尺度特征融合。对遥感小目标检测来说，小目标依赖浅层高分辨率特征，同时也需要高层语义信息，因此可以用它作为“小目标特征增强”的论文依据。

## 迁移到 YOLO11n-OBB 的方案

优先级从高到低：

1. 增加 P2/4 小目标检测层，让模型显式预测更高分辨率特征上的小目标。
2. 在 YOLO neck 的多尺度融合处加入轻量加权融合，替代部分普通 Concat。
3. 如果参数和显存允许，再考虑双向融合路径。

## 风险

- P2 检测层会增加计算量和显存。
- BiFPN 全量照搬会让 YOLO11n 变重，不符合轻量 baseline。
- 消融时要确保提升不是来自更大输入尺寸或训练策略变化。

