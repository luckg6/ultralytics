# 第四章 2024+ 候选改进点筛选

记录日期：2026-07-29

本文件用于第四章 C、D 模块选型。第四章当前 baseline 是：

```text
LSKNet-T Backbone
+ necessary channel adapters
+ original YOLO11 Neck
+ original YOLO11 OBB Head
```

第四章不继承第三章 FSPB/LPCF。LSKNet-T 是基础架构选择，不作为创新。C、D 必须首先相对 LSKNet-T baseline 做受控消融，不以强行超过第三章 A+B 为设计目标。

## 当前 baseline 暴露的问题

DIOR-R official test：

| Model | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|---:|---:|
| Chapter 3 A+B | 2.740 | 10.7 | 72.25 | 54.55 | 29.20 | 20.42 |
| LSKNet-T baseline | 5.728 | 18.7 | 73.72 | 56.88 | 27.69 | 18.15 |

解读：

- LSKNet-T baseline 的全尺度指标有潜力，但参数量和计算量显著更大，不能据此声称其公平优于第三章 A+B 或 YOLO11 原生 backbone。
- 小目标指标仍低于第三章 A+B，说明仅换遥感 backbone 后，细粒度目标和方向/几何定位仍有改进空间。
- C、D 应围绕第四章自己的问题展开：方向敏感特征、几何/角度稳定性、浅层细节与深层语义交互、复杂背景下的类别一致性。

## 候选来源

| 候选 | 代表工作 | 年份/来源 | 论文/代码状态 | 与第四章关系 |
|---|---|---|---|---|
| GRA-style directional calibration | GRA: Detecting Oriented Objects through Group-wise Rotating and Attention | ECCV 2024 | 本地已有 `research/external_repos/GRA` | 针对旋转目标方向变化，适合做 C：方向敏感特征校准 |
| Frequency-aware detail fusion | FreqFusion: Frequency-Aware Feature Fusion for Dense Image Prediction | arXiv 2024 / TPAMI 项目代码 | 本地已有 `research/external_repos/FreqFusion` | 适合做 D：浅深层融合时补边界和高频细节 |
| FDConv-style frequency dynamic convolution | Frequency Dynamic Convolution for Dense Image Prediction | CVPR 2025 | 本地已有 `research/external_repos/FDConv` | 可作为 D 的较重备选：频域动态卷积增强 backbone/adapter 特征 |
| Angle/boundary representation | Rethinking Boundary Discontinuity Problem for Oriented Object Detection | CVPR 2024 | 需进一步下载/核对代码 | 可作为 D 或 loss/head 备选，但要避免和现有 ProbIoU/OBB loss 重复 |
| Point-axis geometry | Projecting Points to Axes: Oriented Object Detection via Point-Axis Representation | ECCV 2024 | 官网有 paper/code 链接，尚未本地化 | 几何辅助监督备选，工程量偏大 |
| CANConv | Content-Adaptive Non-Local Convolution for Remote Sensing Pansharpening | CVPR 2024 | 源码未下载成功；原任务是 pansharpening | 低优先级。遥感属性强，但迁移到检测需要额外论证 |

## 已实现 C：方向感知特征校准模块

暂名：`OAC` / `Orientation-Aware Calibration`。

参考 GRA 的核心动机：旋转目标检测需要捕获随方向变化的细粒度特征。GRA 使用 group-wise rotating 与 attention 来替换 backbone 中的卷积操作，并强调在参数效率下建模方向信息。

第四章中的落点建议：

- 不整体替换 LSKNet-T backbone，避免把 LSKNet-T baseline 改成另一个 backbone。
- 在 LSKNet-T 输出后的 adapter 或 neck 前段插入轻量方向校准，例如对 P3/P4/P5 adapter 输出做方向组 depthwise 分支。
- 只使用标准 PyTorch 算子，不引入自定义 CUDA 或 mmrotate 依赖。
- 重点服务第四章的方向/几何特征建模，不复制第三章 FSPB 的 P2 分支，也不复制 LPCF 的 poly-kernel neck fusion。

第一版建议：

```text
LSKNet-T C3/C4/C5 output
-> 1x1 channel adapter
-> Orientation-Aware Calibration on P3/P4/P5
-> original YOLO11 Neck
-> original YOLO11 OBB Head
```

当前实现：

- 模块：`ultralytics/nn/modules/remote_obb_blocks.py` 中的 `OrientationAwareCalibration`。
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-oac.yaml`。
- 本地配置：`experiments/chapter4/lsknet_t_oac_dior_official.yaml`。
- `/home/ws` 配置：`experiments/chapter4/lsknet_t_oac_dior_official_homews.yaml`，固定 `batch=16`、`device=1`、`cache=ram`。
- 初始化报告：`experiments/chapter4/lsknet_t_oac_init_report.md`。
- 初始化核验：LSKNet-T DOTA backbone 478/478，YOLO11n-OBB compatible neck/head 304/355，Params 5.849M，GFLOPs 19.1。
- 单种子评估记录：`experiments/chapter4/eval_lsknet_t_oac_dior_official_test_2026-07-29.md`。

优点：

- 和第三章 A/B 改动位置不同：更靠近 backbone 输出与原 neck 输入之间。
- 和 LSKNet 本身不同：LSKNet 选择不同范围空间上下文，OAC 侧重显式方向组响应。
- 本地已有 GRA 源码，可直接查实现细节。

风险：

- 之前第三章 C-GRA-Lite 单点在 YOLO11 baseline 上没有成为最优 C，因此第四章不能简单照搬旧 `C3k2GRA`。
- 应换落点和叙事：不是 head/neck C3k2 后处理，而是 LSKNet-T adapter 后的方向校准。
- DIOR-R official 单种子结果显示 All mAP50、Small mAP50、Small mAP50:95 分别提升 +0.30、+1.93、+1.32，但 All mAP50:95 下降 -0.13。OAC 方向有效但还不是四项全优。

## 已实现 D：频率感知细节融合模块

暂名：`FDF` / `Frequency Detail Fusion`。

参考 FreqFusion 的核心动机：层级模型在融合低层高分辨率特征与高层语义特征时，容易出现类内不一致和边界位移；FreqFusion 使用自适应低通、高通和重采样来增强一致性与边界细节。

第四章中的落点建议：

- 不新增第三章式 P2 检测分支。
- 只替换或增强原 YOLO11 neck 中一次或两次上采样融合，例如 P5->P4、P4->P3。
- 做轻量版，不完整搬运 FreqFusion 的全部生成器；第一版可先做高频残差门控 + 低频语义平滑。
- 保持 OBB Head 不变，避免和第三章 head/loss 探索混在一起。

第一版建议：

```text
Upsample(high-level feature) + lateral low-level feature
-> frequency detail gate
-> concat
-> original C3k2
```

优点：

- 针对 LSKNet-T baseline 小目标仍弱的现象：补高频边界和细节。
- 和第三章 A 不同：不增加 P2 预测尺度；和第三章 B 不同：不是 poly-kernel context，而是频域/高低频一致性。
- 可和 C 互补：C 负责方向，D 负责频率细节/融合一致性。

当前实现：

- 模块：`ultralytics/nn/modules/remote_obb_blocks.py` 中的 `FreqDetailFusion`。
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-fdf.yaml`。
- 本地配置：`experiments/chapter4/lsknet_t_fdf_dior_official.yaml`。
- `/home/ws` 配置：`experiments/chapter4/lsknet_t_fdf_dior_official_homews.yaml`，固定 `batch=16`、`device=1`、`cache=ram`。
- 初始化报告：`experiments/chapter4/lsknet_t_fdf_init_report.md`。
- 单种子评估记录：`experiments/chapter4/eval_lsknet_t_fdf_dior_official_test_2026-07-29.md`。

风险：

- 当前是 FreqFusion 启发的轻量近似版，不完整搬运官方 ALPF/AHPF/offset 生成器。
- DIOR-R official 单种子结果显示小目标 mAP50 / mAP50:95 分别提升 +1.64 / +1.32，全尺度 mAP50:95 微升 +0.04，但全尺度 mAP50 下降 -0.13。FDF 方向有效但还不是四项全优。
- 如果后续 C 不能补回全尺度 mAP50，可基于已补齐的 FreqFusion 源码再升级为更接近原论文的 FDF-plus。

## 备选 D：FDConv-style 频域动态卷积

FDConv 是 CVPR 2025 工作，本地源码已齐。其思路是让动态卷积在 Fourier domain 中学习频率多样的权重，并使用 Kernel Spatial Modulation 与 Frequency Band Modulation。

第四章落点建议：

- 替换 adapter 后的 3x3 Conv 或 neck 中少量 C3k2 内部卷积。
- 不全网替换，先在 P3/P4 adapter 后做轻量测试。

优点：

- 源码已齐；
- 2025 顶会；
- 与 LSKNet 的大核空间选择不同，强调频率多样的动态滤波。

风险：

- 原版 FDConv 依赖 mmdet 风格，直接迁移需要瘦身；
- 参数和 GFLOPs 可能进一步上升，需如实报告。

## 低优先级：CANConv

CANConv 是 CVPR 2024 遥感 pansharpening 工作，提出 content-adaptive non-local convolution，利用 spatial adaptability 和 non-local self-similarity。

暂不作为主 C/D：

- 原任务不是检测；
- 官方实现包含子模块/native build 依赖，迁移成本较高；
- 对硕士第四章叙事需要更多论证。

如果后续使用，需要用户手动补齐：

```text
research/external_repos/CANConv/
```

推荐下载地址：

```text
https://github.com/duanyll/CANConv
```

## 当前建议路线

```text
第一优先级：
  D = FDF 已完成单种子训练，主要提升小目标指标
  C = OAC 已完成单种子训练，补回并超过全尺度 mAP50，但 All mAP50:95 略降
  已完成 C+D = OAC+FDF 三 seed DIOR-R official 评估；组合模型在平均 Small mAP50、Small mAP50:95 和 All mAP50:95 上最好，但 All mAP50 平均值由 OAC 单模块最高，且 seed 3407 的组合全尺度指标存在回落

第二优先级：
  若 FreqFusion 材料迟迟不齐，则 D 改为 FDConv-lite，用本地 FDConv 材料做频域动态卷积轻量适配

第三优先级：
  角度连续表示 / Point-Axis / CANConv 作为论文讨论或后续备选，不先实现
```

## 外部来源链接

- PKINet official repo: https://github.com/PKINet/PKINet
- GRA arXiv: https://arxiv.org/abs/2403.11127
- FreqFusion official repo: https://github.com/Linwei-Chen/FreqFusion
- FDConv official repo: https://github.com/Linwei-Chen/FDConv
- Point-Axis project: https://pointaxis.github.io/
- CANConv official repo: https://github.com/duanyll/CANConv
