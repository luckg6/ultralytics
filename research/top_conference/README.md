# 顶会论文与开源代码参考

本目录记录第三章历史探索和第四章候选方法的论文、源码与迁移判断。它是研究索引，不是当前实验结论；当前状态分别以 `paper/ippr2026/main.pdf` 和 `experiments/chapter4/README.md` 为准。

## 章节边界

- 第三章已经定稿为 FSPC-OBB：FSPB(A) + LPCF(B)。C-GRA、C-Chol、C-SET-HBS 等均为历史探索，不进入第三章主方法。
- 第四章以 LSKNet-T 混合结构为 baseline，LSKNet-T 本身不算创新。OAC/FDF 第一轮组合、Blend 与 FDConv-Lite 均已完成筛选但未达到最终组合目标。
- 第四章最新筛选显示：SGC 为 Strip R-CNN 启发的条带几何校准候选，单模块在 DIOR-R seed 42 上有效；直接 `SGC+FDF` 组合存在负交互，不继续扩展。当前新增 `FDR-Lite` 作为更温和的频率细节残差 D 候选，并配置 `SGC+FDR-Lite` 组合；在通过 seed 42、多 seed 和第二数据集验证前，不把它写成最终 C/D。

## 参考索引

| 目录 | 论文/模块 | 来源 | 当前用途 |
|---|---|---|---|
| `lsknet/` | Large Selective Kernel Network | ICCV 2023 | 第四章 baseline backbone 依据 |
| `pkinet_2024/` | PKINet / Poly Kernel Inception | CVPR 2024 | 第三章 LPCF 研究参考 |
| `gra_2024/` | Group-wise Rotating and Attention | ECCV 2024 | OAC 历史筛选依据 |
| `freqfusion_2024/` | FreqFusion | 2024 / 后续期刊项目 | 第四章 FDF 候选依据 |
| `fdconv_2025/` | Frequency Dynamic Convolution | CVPR 2025 | FDConv-Lite 历史筛选依据 |
| `strip_rcnn_2025/` | Strip R-CNN / Large Strip Convolution | arXiv 2025 / AAAI 2026 | 下一轮 SGC 候选依据 |
| `gaucho_2025/` | GauCho | CVPR 2025 | OBB 几何表示备选 |
| `canconv_2024/` | CANConv | CVPR 2024 | 低优先级跨任务备选 |
| `set_2025/` | SET / HBS | CVPR 2025 | 第三章 C 系列历史探索 |
| `efficientdet_bifpn/`、`dynamic_head/`、`internimage_dcnv3/` | 早期多尺度/动态结构 | 2020-2023 | 历史参考，不是当前路线 |
| `yolov10_2024/` | YOLOv10 | NeurIPS 2024 | 效率和训练分配参考 |

第四章候选的完整筛选依据见 `chapter4_2024plus_candidates.md`；第三章早期 C 系列过程见 `2024_plus_experiment_plan.md`，该文件已冻结为历史记录。

## 外部源码约定

完整第三方仓库放在 `research/external_repos/`，默认不并入主项目。真正落地时只抽取必要思想到项目模块与 YAML，并记录来源、结构差异和许可证。当前下载状态以 `research/external_repos/DOWNLOAD_STATUS.md` 为准。
