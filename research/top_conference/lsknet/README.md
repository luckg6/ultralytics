# LSKNet

## 基本信息

- 论文：Large Selective Kernel Network for Remote Sensing Object Detection
- 会议：ICCV 2023
- 论文链接：https://openaccess.thecvf.com/content/ICCV2023/html/Li_Large_Selective_Kernel_Network_for_Remote_Sensing_Object_Detection_ICCV_2023_paper.html
- PDF：https://openaccess.thecvf.com/content/ICCV2023/papers/Li_Large_Selective_Kernel_Network_for_Remote_Sensing_Object_Detection_ICCV_2023_paper.pdf
- 官方代码：https://github.com/zcablii/LSKNet

## 可借鉴点

LSKNet 专门面向遥感目标检测，强调遥感目标需要动态选择不同范围的上下文信息。这个动机非常适合 DIOR-R、DOTA 这类复杂背景、尺度变化明显的遥感数据集。

## 迁移到 YOLO11n-OBB 的方案

优先级从高到低：

1. 抽取轻量 LSK block，放在 backbone 后段或 SPPF 前后。
2. 放在 neck 融合后的高层特征处，增强上下文表达。
3. 如果小目标提升明显，再尝试放到 P3/P4 融合路径。

## 风险

- 大核卷积可能增加计算量。
- 如果放太多 LSK block，会破坏 YOLO11n 的轻量特点。
- 需要在论文中强调“遥感上下文选择”，避免写成普通注意力堆叠。

