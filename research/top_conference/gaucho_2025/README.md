# GauCho / Gaussian Distributions with Cholesky Decomposition

## 基本信息

- 论文：GauCho: Gaussian Distributions with Cholesky Decomposition for Oriented Object Detection
- 会议：CVPR 2025
- 论文链接：https://openaccess.thecvf.com/content/CVPR2025/html/Marques_GauCho_Gaussian_Distributions_with_Cholesky_Decomposition_for_Oriented_Object_Detection_CVPR_2025_paper.html
- PDF：https://openaccess.thecvf.com/content/CVPR2025/papers/Marques_GauCho_Gaussian_Distributions_with_Cholesky_Decomposition_for_Oriented_Object_Detection_CVPR_2025_paper.pdf
- 官方代码：https://github.com/jhlmarques/GauCho

## 为什么适合本项目

GauCho 针对 OBB 角度边界不连续问题，使用 Cholesky 分解直接预测二维高斯分布参数。当前项目的 A/B/C 都主要改特征表达，尚未触碰 OBB 回归表示。GauCho 可以作为一个更偏“旋转框回归头/损失”的创新方向，用于增强长条目标和角度敏感类别。

## 可迁移方案

优先级从高到低：

1. 先不改 Ultralytics OBB 解码主流程，只阅读其 head/loss 设计，判断是否能做兼容损失。
2. 如果可行，增加一个训练期辅助 loss，把 OBB 转为 Gaussian 表示后约束协方差/方向一致性。
3. 真正替换 OBB head 是高风险方案，放在论文主实验之后。

## 适合作为哪个实验

- C 后续高风险版：`C-GaussianOBB`。
- 更适合作为“讨论/后续工作”或论文扩展实验，不建议立刻替换当前 C。

## 风险

- 需要深入改 OBB head、loss 和后处理，影响面大。
- 与 Ultralytics 当前 OBB 表示耦合较深，调试成本高。
- 当前论文周期里优先做轻量辅助 loss，而不是完整 GauCho head。
