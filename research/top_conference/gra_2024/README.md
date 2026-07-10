# GRA / Group-wise Rotating and Attention

## 基本信息

- 论文：GRA: Detecting Oriented Objects through Group-wise Rotating and Attention
- 会议：ECCV 2024
- 论文链接：https://arxiv.org/abs/2403.11127
- PDF：https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/02600.pdf
- 官方代码：https://github.com/wangjiangshan0725/GRA

## 为什么适合本项目

GRA 直接面向 oriented object detection，提出 group-wise rotating 与 group-wise attention，用较轻量的方式增强方向敏感特征。当前 C-Dynamic 已经证明方向几何感知有一点正向收益，但幅度很小；GRA 可以作为 C 的第二版参考，把“方向感知”做得更贴近旋转目标本身。

## 可迁移方案

优先级从高到低：

1. 做 `GRAConvLite`：把输入通道分组，每组使用不同方向的 depthwise 卷积核或可学习方向调制，不引入自定义 CUDA。
2. 做 `C3k2GRA`：只替换 OBB head 的 P3/P4/P5 融合层，保持检测头层号不变。
3. 若实现旋转卷积成本偏高，则退化成水平、垂直、对角方向的多分支 depthwise 卷积 + group attention。

## 适合作为哪个实验

- C 第二版候选：`C-GRA-Lite`。
- 如果 A+C-Dynamic 小幅提升，可以进一步尝试 `A + C-GRA-Lite`。

## 风险

- 官方实现依赖 ARC/LSKNet 体系，且包含 C++/CUDA 文件，不能直接整体迁移。
- 旋转卷积若用真实 kernel rotation，可能带来实现复杂度和速度损失。
- 论文中要强调这是 GRA 思想的轻量适配，而不是复现完整 GRA。
