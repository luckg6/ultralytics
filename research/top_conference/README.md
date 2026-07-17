# 顶会论文与开源代码参考

这个目录用于沉淀后续 3 个创新点可能参考的顶会论文、官方开源代码和迁移到 YOLO11n-OBB 的计划。

当前不直接把第三方大型代码仓库复制进来，原因是：

- 顶会开源项目通常体量大、依赖复杂，直接放入本仓库会污染实验代码。
- 不同项目许可证不同，正式抽取代码前需要确认许可证兼容性。
- 本论文目标是轻量改进 YOLO11n-OBB，优先抽取必要模块思想，而不是整体替换模型。

## 候选方向

| 目录 | 论文/模块 | 会议 | 对应创新点 | 优先级 |
| --- | --- | --- | --- | --- |
| `efficientdet_bifpn/` | EfficientDet / BiFPN | CVPR 2020 | 小目标多尺度特征融合 | 高 |
| `lsknet/` | Large Selective Kernel Network | ICCV 2023 | 遥感上下文注意力 | 高 |
| `internimage_dcnv3/` | InternImage / DCNv3 | CVPR 2023 | 动态空间采样/几何适应 | 中 |
| `dynamic_head/` | Dynamic Head | CVPR 2021 | 检测头注意力备选 | 中 |
| `pkinet_2024/` | PKINet / Poly Kernel Inception | CVPR 2024 | 遥感多尺度大核上下文 | 高 |
| `gra_2024/` | GRA / Group-wise Rotating and Attention | ECCV 2024 | 旋转目标方向感知卷积，已落地为 C-GRA-Lite | 高 |
| `freqfusion_2024/` | FreqFusion | TPAMI 2024 | 频率感知 neck 特征融合 | 高 |
| `fdconv_2025/` | FDConv | CVPR 2025 | 频域动态卷积 | 中 |
| `gaucho_2025/` | GauCho | CVPR 2025 | OBB 回归表示/角度边界问题 | 中 |
| `set_2025/` | SET / HBS | CVPR 2025 | 小目标背景高频抑制，已落地为 C-SET-HBS | 高 |
| `canconv_2024/` | CANConv | CVPR 2024 | 遥感内容自适应非局部卷积 | 中 |
| `yolov10_2024/` | YOLOv10 | NeurIPS 2024 | 轻量检测器效率/训练分配参考 | 低 |

## 建议落地顺序

1. A-P2 已经验证有效，保留为当前最强单点改进。
2. B-LSK 当前无效，新版 B-PKI-Lite 已替代旧 B，并在 A+B 融合中取得当前最佳结果。
3. C-GRA-Lite、C-Chol-Lite 和两组旧 ABC 均已完成，但没有让 ABC 超过 A+B-PKI-Lite。
4. 当前优先训练 A+B-PKI-Lite+C-SET-HBS：参考 CVPR 2025 SET 的 HBS，以训练期背景平滑辅助监督改善小目标和全尺度检测，推理保持 AB。
5. FDConv、GauCho 完整 head 和 YOLOv10 继续作为备选，不在同一轮叠加。

## 外部源码放置约定

第三方仓库不直接提交进本仓库。若需要本地查看源码，统一浅克隆到：

```text
research/external_repos/
```

该目录默认被 Git 忽略，只保留 `README.md` 和 `.gitignore`。真正实现时，只抽取必要模块到 `ultralytics/nn/modules/remote_obb_blocks.py` 或独立的项目模块文件中，并在对应实验 YAML 中登记结构差异。
