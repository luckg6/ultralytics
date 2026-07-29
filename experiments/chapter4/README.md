# 第四章实验入口

第四章是与第三章并列互补的技术路线，不再定位为解决第三章计算量上升的问题，也不要求最终模型必须全面超过第三章 A+B。

第四章当前基础结构为：

```text
LSKNet-T Backbone
+ necessary channel adapters
+ original YOLO11 Neck
+ original YOLO11 OBB Head
```

该 baseline 不继承第三章的 FSPB 和 LPCF。LSKNet-T 与通道适配只作为第四章基础架构，不作为创新点；后续 C、D 才是第四章创新模块。

第四章定位为：基于遥感专用自适应感受野骨干的精度增强型旋转目标检测方法。

## 与第三章的关系

第三章关注轻量 YOLO11n-OBB 上的 Neck/Head 小目标增强，核心是 FSPB 和 LPCF。

第四章关注 Backbone 特征提取阶段，研究遥感专用自适应感受野、长程空间关系和复杂背景表达。

跨章节结果只用于说明两条路线的特点和权衡，不能作为同容量公平排名：

- 第三章：较低模型复杂度下的小目标检测增强路线；
- 第四章：容量更高、精度优先的复杂场景特征提取路线。

## 第一阶段配置

| 环境 | 配置 | 说明 |
|---|---|---|
| 本地 | `experiments/chapter4/lsknet_t_baseline_dior_official.yaml` | `batch=4`、`cache=disk`、`device=0` |
| `/home/ws` | `experiments/chapter4/lsknet_t_baseline_dior_official_homews.yaml` | `batch=16`、`cache=ram`、`device=1` |

首次训练前先生成混合初始化权重：

```bash
python scripts/prepare_lsknet_yolo_init.py --model ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml
```

然后开始训练：

```bash
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official.yaml
```

服务器上使用：

```bash
python scripts/prepare_lsknet_yolo_init.py --model ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews.yaml
```

## 初始化记录

- LSKNet-T 四个 stage 输出：stride `4/8/16/32`，通道 `32/64/160/256`。
- DOTA checkpoint 的 `backbone.*` 权重加载成功率：478/478。
- YOLO11n-OBB neck/head 兼容权重加载：304/355。
- 随机初始化模块主要为 P3/P4 通道适配层和分类分支。
- 初始化报告：`experiments/chapter4/lsknet_t_baseline_init_report.md`。

## 已完成结果

### DIOR-R official single-seed baseline

- Run directory: `runs/obb/dior_official_lsknet_t_baseline/`
- 评估记录：`experiments/chapter4/eval_lsknet_t_baseline_dior_official_test_2026-07-29.md`
- 训练参数：`device=1`、`batch=16`、`cache=ram`、`epochs=100`、`seed=42`
- 训练期最优 val mAP50-95：0.66724，出现在 epoch 99。
- Test 指标如下，精度为百分数：

| Model | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|---:|---:|
| YOLO11n-OBB baseline | 2.658 | 6.6 | 71.11 | 54.31 | 27.32 | 17.96 |
| Chapter 3 A+B | 2.740 | 10.7 | 72.25 | 54.55 | 29.20 | 20.42 |
| LSKNet-T baseline | 5.728 | 18.7 | 73.72 | 56.88 | 27.69 | 18.15 |

相对于第三章 A+B，LSKNet-T baseline 参数量约为 2.09 倍，GFLOPs 约为 1.75 倍；All mAP50:95 高 2.33，但 Small mAP50:95 低 2.27。因此该结果不能作为“LSKNet-T 优于第三章 A+B”或“LSKNet-T backbone 优于 YOLO11 原生 backbone”的证据。

当前可确认的结论：

1. LSKNet-T 的 DOTA 权重和 YOLO11 Neck/OBB Head 混合结构接入成功；
2. 新 baseline 可以稳定训练和收敛；
3. LSKNet-T baseline 具有较强的全尺度检测潜力；
4. 小目标检测能力仍低于第三章 A+B；
5. 该 baseline 可以继续作为第四章候选基础模型。

## 后续 C/D 设计原则

第四章后续 C、D 首先与自己的 LSKNet-T baseline 做消融，而不是为了强行超过第三章 A+B 来设计。

2024+ 顶会候选改进点已记录在 `research/top_conference/chapter4_2024plus_candidates.md`。当前建议优先考虑：

- C：基于 ECCV 2024 GRA 思路的 LSKNet adapter 后方向感知特征校准；
- D：基于 FreqFusion/FDConv 思路的频率感知细节融合或频域动态卷积轻量适配。

### 已配置：D-FDF

FDF 是 FreqFusion 启发的轻量频率细节融合模块，用于替换 LSKNet-T baseline 原 top-down neck 中的两次 `Upsample + Concat`。它保留原始 YOLO11 OBB Head，不加入第三章 FSPB/LPCF，也不新增 P2 检测分支。

| 环境 | 配置 | 说明 |
|---|---|---|
| 本地 | `experiments/chapter4/lsknet_t_fdf_dior_official.yaml` | `batch=4`、`cache=disk`、`device=0` |
| `/home/ws` | `experiments/chapter4/lsknet_t_fdf_dior_official_homews.yaml` | `batch=16`、`cache=ram`、`device=1` |

训练前已生成专属初始化权重：

```text
weights/pretrained/lsknet/yolo11n_obb_lsknet_t_fdf_hybrid_init.pt
```

初始化核验：

- LSKNet-T DOTA backbone keys loaded: 478/478；
- YOLO11n-OBB compatible neck/head keys loaded: 304/355；
- Params: 5.794M；
- GFLOPs: 19.0。

本地训练：

```bash
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdf_dior_official.yaml
```

`/home/ws` 训练：

```bash
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_fdf_dior_official_homews.yaml
```

C、D 应围绕第四章自己的问题展开，例如：

- LSKNet-T baseline 对小目标细粒度信息利用不足；
- 旋转目标方向和几何特征建模不足；
- 浅层细节与深层大感受野语义之间交互不足；
- 复杂背景下类别判别或旋转框定位不足。

C、D 不应简单重复 LSKNet 已有的大核上下文机制，也不要直接复制第三章 FSPB、LPCF 或再增加一个完全相同的高分辨率预测分支。

第四章成立的核心条件：

- C 单独相对 LSKNet-T baseline 稳定提升；
- D 单独相对 LSKNet-T baseline 稳定提升；
- C+D 优于 LSKNet-T baseline；
- 主要提升在两个数据集和多随机种子下具有稳定性；
- Params、GFLOPs、FPS、延迟和显存完整报告，但不预设必须下降。
