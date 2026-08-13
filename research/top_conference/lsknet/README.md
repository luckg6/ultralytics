# LSKNet

## 基本信息

- 论文：Large Selective Kernel Network for Remote Sensing Object Detection
- 会议：ICCV 2023
- 论文页面：https://openaccess.thecvf.com/content/ICCV2023/html/Li_Large_Selective_Kernel_Network_for_Remote_Sensing_Object_Detection_ICCV_2023_paper.html
- PDF：https://openaccess.thecvf.com/content/ICCV2023/papers/Li_Large_Selective_Kernel_Network_for_Remote_Sensing_Object_Detection_ICCV_2023_paper.pdf
- 官方代码：https://github.com/zcablii/LSKNet

## 在本项目中的定位

LSKNet 面向遥感目标检测提出大选择核机制，强调遥感目标需要根据场景动态选择不同范围的上下文信息。

第四章采用 LSKNet-T 作为基础 backbone，定位为“基于遥感专用自适应感受野骨干的精度增强型旋转目标检测方法”。它与第三章不是严格递进关系，而是并列互补路线：

- 第三章：基于 YOLO11n-OBB，从 Neck 和 Head/预测端增强小目标细粒度特征传递与预测。
- 第四章：基于 LSKNet-T，从 Backbone 特征提取源头增强复杂遥感场景的自适应感受野和上下文表达。

LSKNet-T backbone 替换和必要通道适配只作为第四章基础架构选择，不作为本文创新点。第四章创新点只来自最终经受控实验确认的 C、D 两个模块。

## 本地材料状态

| 材料 | 本地路径 | 状态 |
|---|---|---|
| LSKNet 源码 | `research/external_repos/LSKNet/` | 已确认 `README.md`、`mmrotate/models/backbones/lsknet.py`、`configs/lsknet/lsk_t_fpn_1x_dota_le90.py` 存在 |
| DOTA LSKNet-T + Oriented R-CNN checkpoint | `weights/pretrained/lsknet/lsk_t_fpn_1x_dota_le90_20230206-3ccee254.pth` | 已读取成功 |
| ImageNet LSKNet-T backbone checkpoint（备用） | `weights/pretrained/lsknet/lsk_t_backbone.pth.tar` | 已读取成功，备用 |

## 官方 LSKNet-T 核验摘要

- 官方配置：`embed_dims=[32, 64, 160, 256]`，`depths=[3, 3, 5, 2]`。
- DOTA checkpoint 文件大小：84,128,596 bytes。
- DOTA checkpoint 顶层 key：`meta`、`state_dict`。
- DOTA checkpoint `state_dict` 共 508 个 key，其中 `backbone.*` 共 478 个 key。
- DOTA checkpoint 总 tensor 参数量：21,002,742；可提取的 `backbone.*` 参数量：3,997,644。
- ImageNet checkpoint 文件大小：68,626,267 bytes；为纯 backbone 风格 key，无 `backbone.` 前缀；tensor 参数量：4,254,644。

## 当前实现状态

已完成第一阶段 baseline 的结构与初始化：

- 模块实现：`ultralytics/nn/modules/remote_obb_blocks.py` 中的 `LSKNetT`。
- 模型 YAML：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml`。
- 初始化脚本：`scripts/prepare_lsknet_yolo_init.py`。
- 初始化报告：`experiments/chapter4/lsknet_t_baseline_init_report.md`。
- 本地训练配置：`experiments/chapter4/lsknet_t_baseline_dior_official.yaml`。
- `/home/ws` 训练配置：`experiments/chapter4/lsknet_t_baseline_dior_official_homews.yaml`。

当前 baseline 结构为：

```text
LSKNet-T Backbone
+ P3/P4 1x1 channel adapters
+ original YOLO11n-OBB SPPF/C2PSA
+ original YOLO11n-OBB PAN neck
+ original YOLO11n-OBB OBB head
```

它不包含第三章 FSPB、LPCF 或 P2 OBB 检测分支。

## 初始化核验结果

使用 `scripts/prepare_lsknet_yolo_init.py` 生成混合初始化权重：

- 输出权重：`weights/pretrained/lsknet/yolo11n_obb_lsknet_t_hybrid_init.pt`。
- LSKNet-T 输出：
  - C2：`(1, 32, 160, 160)`
  - C3：`(1, 64, 80, 80)`
  - C4：`(1, 160, 40, 40)`
  - C5：`(1, 256, 20, 20)`
- DOTA backbone 权重加载：478/478。
- YOLO11n-OBB neck/head 权重加载：304/355。
- YOLO 未加载项集中在 `model.23.cv3.*` 分类分支，原因是源权重类别头与当前 YAML 默认类别数/通道不匹配；训练到 DIOR-R 时分类分支会按数据集类别重新初始化。
- 随机初始化模块：
  - `model.5.*`：P3 adapter；
  - `model.6.*`：P4 adapter；
  - `model.21.cv3.*`：分类分支。
- 模型规模：376 layers，5,763,985 params，18.9 GFLOPs at 640。

## DIOR-R Official 单种子结果

2026-07-29 已完成纯 LSKNet-T baseline 训练。保留权重已整理到 `weights/checkpoints/chapter4/dior_official/seed42/baseline/best.pt`，评估记录见 `experiments/chapter4/eval_lsknet_t_baseline_dior_official_test_2026-07-29.md`。

| Model | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|---:|---:|
| YOLO11n-OBB baseline | 2.658 | 6.6 | 71.11 | 54.31 | 27.32 | 17.96 |
| Chapter 3 A+B | 2.740 | 10.7 | 72.25 | 54.55 | 29.20 | 20.42 |
| LSKNet-T baseline | 5.728 | 18.7 | 73.72 | 56.88 | 27.69 | 18.15 |

正确解读：

- LSKNet-T 的 DOTA 权重和 YOLO11 Neck/OBB Head 的混合结构已经接入成功。
- 新 baseline 可以稳定训练和收敛。
- LSKNet-T baseline 具有较强的全尺度检测潜力。
- 小目标检测能力仍低于第三章 A+B。
- 由于参数量和 GFLOPs 明显高于第三章 A+B，不能把该结果写成“LSKNet-T baseline 优于第三章 A+B”。
- 该 baseline 可以继续作为第四章候选基础模型。

## 使用命令

本地：

```bash
python scripts/prepare_lsknet_yolo_init.py --model ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official.yaml
```

`/home/ws` 服务器：

```bash
python scripts/prepare_lsknet_yolo_init.py --model ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews.yaml
```

## C/D 约束与当前状态

- LSKNet-S 暂不作为第四章主方案，最多保留为后续骨干选择对比项。
- C、D 首先与 LSKNet-T baseline 做内部消融，不以强行超过第三章 A+B 为设计目标。
- C、D 不应简单重复 LSKNet 已有的大核上下文机制。
- C、D 不应直接复制第三章 FSPB、LPCF 或完全相同的高分辨率预测分支。
- Params、GFLOPs、FPS/latency 和显存占用必须如实记录，但不要求一定低于第三章。

OAC、FDF、OAC+FDF、Blend 与 FDConv-Lite 已完成筛选，但组合没有稳定优于单模块，因此不作为定稿 C/D。当前待验证路线为 `SGC + FDF`，详见 `experiments/chapter4/README.md`；在训练结果产生前，它仍是候选而非论文结论。
