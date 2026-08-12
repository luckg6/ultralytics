# CANConv / Content-Adaptive Non-Local Convolution

## 基本信息

- 论文：Content-Adaptive Non-Local Convolution for Remote Sensing Pansharpening
- 会议：CVPR 2024
- 论文链接：https://arxiv.org/abs/2404.07543
- PDF：https://openaccess.thecvf.com/content/CVPR2024/papers/Duan_Content-Adaptive_Non-Local_Convolution_for_Remote_Sensing_Pansharpening_CVPR_2024_paper.pdf
- 官方代码：https://github.com/duanyll/CANConv

## 为什么适合本项目

CANConv 虽然不是检测论文，但它是 CVPR 2024 的遥感图像工作，强调内容自适应卷积和非局部自相似。DIOR-R 的复杂背景、密集目标和纹理干扰明显，CANConv 的思想可以作为 B-LSK 失败后的遥感上下文新路线。

## 可迁移方案

优先级从高到低：

1. 做 `CANLite`：用局部窗口相似性或全局池化近似非局部关系，避免完整 SRP/PWAC 复杂实现。
2. 只放在 SPPF 后或 P4/P5 neck 融合处，不进入 P2 分支。
3. 与 PKINet 二选一，不要同时堆多个上下文模块。

## 适合作为哪个实验

- 低优先级后备研究方向；不是第三章 B，也不是第四章当前 C/D。源码尚未完整准备。

## 风险

- 原任务是 pansharpening，不是检测；论文动机迁移需要解释为“遥感图像非局部纹理与背景抑制”。
- 非局部计算可能重，必须严格限制窗口和通道。
- 优先级低于 PKINet 和 FreqFusion。
