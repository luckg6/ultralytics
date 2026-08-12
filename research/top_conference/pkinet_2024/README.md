# PKINet / Poly Kernel Inception Network

## 基本信息

- 论文：Poly Kernel Inception Network for Remote Sensing Detection
- 会议：CVPR 2024
- 论文链接：https://openaccess.thecvf.com/content/CVPR2024/html/Cai_Poly_Kernel_Inception_Network_for_Remote_Sensing_Detection_CVPR_2024_paper.html
- PDF：https://openaccess.thecvf.com/content/CVPR2024/papers/Cai_Poly_Kernel_Inception_Network_for_Remote_Sensing_Detection_CVPR_2024_paper.pdf
- 官方代码：https://github.com/PKINet/PKINet
- 许可证：Apache-2.0

## 为什么适合本项目

PKINet 是面向遥感检测的 CVPR 2024 工作，核心动机是用多种大核/多尺度卷积增强遥感目标的尺度鲁棒性。本项目据此完成了第三章 LPCF 的轻量迁移，替代了无效的早期 B-LSK。

## 可迁移方案

优先级从高到低：

1. 不替换完整 backbone，只抽取轻量 PKI block，放在 P3/P4 neck 融合后的 `C3k2` 或 `C2PSA` 附近。
2. 做成 `C3k2PKI`，用 3x3、5x5 depthwise、大核 depthwise 的并联分支，再用 1x1 压回原通道。
3. 先只替换 OBB head 的 P3/P4 两个融合层，避免像 A-P2 一样显存压力过大。

## 适合作为哪个实验

- 第三章已定稿 B：`LPCF`，内部历史名 `B-PKI-Lite`。
  - 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-b-pki-lite.yaml`
  - 本地配置：`experiments/dior/b_pki_lite.yaml`
  - 服务器配置：`experiments/dior/b_pki_lite_homews.yaml`
  - 模块：`C3k2PKI` / `PKIContext`
  - 位置：top-down neck 的 P5->P4、P4->P3 融合块
- 第三章最终组合为 FSPB + LPCF，不再扩展旧 B-LSK 或第三个 C 模块。

## 风险

- 原仓库基于 MMRotate/MMDetection，不能整体搬入本项目。
- 多分支大核可能提高显存和延迟，需要用 depthwise 和小通道比例控制开销。
- 建议先做 head/neck 局部替换，不做全 backbone 替换。
