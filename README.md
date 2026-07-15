# YOLO11n-OBB 遥感小目标检测实验仓库

本仓库基于 Ultralytics YOLO 源码，用于完成一篇面向 EI 会议的论文，并服务后续毕业学位论文。研究对象是遥感影像小目标的 OBB 旋转框检测。当前主线任务是以 YOLO11n-OBB 为基础模型，在 DIOR-R 和第二个遥感 OBB 数据集上完成 baseline、三个创新点和融合消融实验。

## 研究目标

- 任务：遥感图像小目标检测，采用 OBB 旋转框检测形式。
- 论文定位：EI 会议论文 + 毕业学位论文。
- 基础模型：`weights/pretrained/yolo11n-obb.pt`。
- 主数据集：DIOR-R。
- 第二数据集候选：DOTA-v1.0 或 HRSC2016。
- 论文实验目标：设计 3 个轻量、可解释、可消融的模型改进点，并验证单独改进和组合改进的效果。

## 当前 Baseline

DIOR-R baseline 使用以下流程：

```text
weights/pretrained/yolo11n-obb.pt -> DIOR-R 训练 -> weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt
```

当前训练脚本：

```bash
python scripts/train_obb.py --config experiments/dior/baseline.yaml
```

旧的硬编码训练脚本已清理，后续新增实验统一使用 `scripts/train_obb.py` 和 `experiments/` 下的实验配置。

当前 DIOR-R baseline 关键设置：

- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-baseline.yaml`
- 预训练权重：`weights/pretrained/yolo11n-obb.pt`
- 数据集配置：`DIOR.yaml`
- 训练轮数：`epochs=100`
- 输入尺寸：`imgsz=640`
- batch：`batch=4`
- 随机种子：`seed=42`
- 确定性训练：`deterministic=True`
- 缓存：`cache='disk'`
- 学习率策略：`cos_lr=True`

说明：最初 baseline 和 A-P2 尝试过更大的 batch，但本机 RTX 4060 Laptop 8GB 在 A-P2 上出现 OOM 和 CPU fallback；显存占用仍偏高。后续主实验统一改为 `batch=4`，确保 baseline/A/B/C/AB/ABC 比较公平。

当前 DIOR-R baseline 对应的原始训练日志为 `runs/obb/train10/results.csv`，验证指标约为：

- mAP50：0.849
- mAP50-95：0.670

## 当前 DIOR-R 阶段结果

A-P2、B-LSK、C-Dynamic、C-Dynamic-Plus、C-GRA-Lite、C-Chol-Lite、B-PKI-Lite、A+B-PKI-Lite 和 A+B-PKI-Lite+C-Plus 已完成 `test` split 评估。A-P2 相对 baseline 有稳定提升，尤其是小目标指标提升明显；B-LSK 当前单独实验未带来提升；C-Chol-Lite 是当前最好的 C 单点，全尺度 mAP50-95 和小目标 mAP50-95 均超过 C-Dynamic-Plus；新版 B-PKI-Lite 轻微正向；A+B-PKI-Lite 进一步超过 A-P2，是当前 DIOR-R test 上的最佳结果。A+B-PKI-Lite+C-Plus 相比 baseline 仍明显提升，但低于 A+B-PKI-Lite，可作为三创新点融合消融记录。下一步可训练 A+B-PKI-Lite+C-Chol-Lite，验证新的 C 是否能改善 ABC 组合。

| 模型 | 权重路径 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---|---:|---:|---:|---:|---:|---:|
| Baseline | `weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt` | 2,657,623 | 6.6 | 0.8588 | 0.6874 | 0.5146 | 0.3470 |
| A-P2 | `weights/experiments/dior/a_p2/best.pt` | 2,698,340 | 10.5 | 0.8779 | 0.6990 | 0.5830 | 0.4215 |
| B-LSK | `weights/experiments/dior/b_lsk/best.pt` | 2,776,094 | 6.7 | 0.8580 | 0.6809 | 0.5070 | 0.3438 |
| B-PKI-Lite | `weights/experiments/dior/b_pki_lite/best.pt` | 2,699,673 | 6.8 | 0.8588 | 0.6885 | 0.5249 | 0.3621 |
| C-Dynamic | `weights/experiments/dior/c_dynamic/best.pt` | 2,676,940 | 6.6 | 0.8562 | 0.6884 | 0.5173 | 0.3527 |
| C-Dynamic-Plus | `weights/experiments/dior/c_dynamic_plus/best.pt` | 2,696,431 | 6.7 | 0.8588 | 0.6896 | 0.5268 | 0.3541 |
| C-GRA-Lite | `weights/experiments/dior/c_gra_lite/best.pt` | 2,713,135 | 6.7 | 0.8583 | 0.6861 | 0.5219 | 0.3522 |
| C-Chol-Lite | `weights/experiments/dior/c_chol_lite/best.pt` | 2,729,296 | 6.6 | 0.8577 | 0.6902 | 0.5282 | 0.3589 |
| A+B-PKI-Lite | `weights/experiments/dior/ab_p2_pki_lite/best.pt` | 2,740,390 | 10.7 | 0.8859 | 0.7198 | 0.5958 | 0.4288 |
| A+B-PKI-Lite+C-Plus | `weights/experiments/dior/abc_p2_pki_geo_plus/best.pt` | 2,784,390 | 11.1 | 0.8832 | 0.7149 | 0.5838 | 0.4242 |
| A-P2 相对 baseline | - | +40,717 | +3.9 | +0.0191 | +0.0116 | +0.0684 | +0.0745 |
| B-LSK 相对 baseline | - | +118,471 | +0.1 | -0.0008 | -0.0065 | -0.0076 | -0.0032 |
| B-PKI-Lite 相对 baseline | - | +42,050 | +0.2 | +0.0000 | +0.0011 | +0.0103 | +0.0151 |
| C-Dynamic 相对 baseline | - | +19,317 | +0.0 | -0.0026 | +0.0010 | +0.0027 | +0.0057 |
| C-Dynamic-Plus 相对 baseline | - | +38,808 | +0.1 | +0.0000 | +0.0022 | +0.0122 | +0.0071 |
| C-GRA-Lite 相对 baseline | - | +55,512 | +0.1 | -0.0005 | -0.0013 | +0.0073 | +0.0052 |
| C-Chol-Lite 相对 baseline | - | +71,673 | +0.0 | -0.0011 | +0.0028 | +0.0136 | +0.0119 |
| A+B-PKI-Lite 相对 baseline | - | +82,767 | +4.1 | +0.0271 | +0.0324 | +0.0812 | +0.0818 |
| A+B-PKI-Lite+C-Plus 相对 baseline | - | +126,767 | +4.5 | +0.0244 | +0.0275 | +0.0692 | +0.0772 |

轻量化对比：A-P2、B-PKI-Lite、C-Dynamic、C-Dynamic-Plus、C-GRA-Lite、C-Chol-Lite 相对 baseline 的参数增幅分别为 +1.53%、+1.58%、+0.73%、+1.46%、+2.09%、+2.70%；A+B-PKI-Lite 的评估摘要参数量为 2,740,390，相对 baseline 增加 82,767，增幅 +3.11%；A+B-PKI-Lite+C-Plus 的评估摘要参数量为 2,784,390，相对 baseline 增加 126,767，增幅 +4.77%。

对应记录文件：

- `weights/experiments/dior/a_p2/eval_dior_test_2026-07-06.md`
- `weights/baselines/dior-r/eval_dior_test_2026-07-06.md`
- `weights/experiments/dior/a_p2/compare_with_baseline_dior_test_2026-07-06.md`
- `weights/experiments/dior/b_lsk/eval_dior_test_2026-07-09.md`
- `weights/experiments/dior/b_lsk/compare_with_baseline_a_p2_dior_test_2026-07-09.md`
- `weights/experiments/dior/c_dynamic/eval_dior_test_2026-07-10.md`
- `weights/experiments/dior/c_dynamic/compare_with_baseline_a_p2_b_lsk_dior_test_2026-07-10.md`
- `weights/experiments/dior/c_dynamic_plus/eval_dior_test_2026-07-14.md`
- `weights/experiments/dior/c_dynamic_plus/compare_with_baseline_c_dior_test_2026-07-14.md`
- `weights/experiments/dior/c_gra_lite/eval_dior_test_2026-07-15.md`
- `weights/experiments/dior/c_gra_lite/compare_with_baseline_cplus_ab_dior_test_2026-07-15.md`
- `weights/experiments/dior/c_chol_lite/eval_dior_test_2026-07-15.md`
- `weights/experiments/dior/c_chol_lite/compare_with_baseline_cplus_ab_dior_test_2026-07-15.md`
- `weights/experiments/dior/b_pki_lite/eval_dior_test_2026-07-11.md`
- `weights/experiments/dior/b_pki_lite/compare_with_baseline_a_b_lsk_c_dior_test_2026-07-11.md`
- `weights/experiments/dior/ab_p2_pki_lite/eval_dior_test_2026-07-13.md`
- `weights/experiments/dior/ab_p2_pki_lite/compare_with_baseline_a_b_pki_c_dior_test_2026-07-13.md`
- `weights/experiments/dior/abc_p2_pki_geo_plus/eval_dior_test_2026-07-14.md`
- `weights/experiments/dior/abc_p2_pki_geo_plus/compare_with_baseline_ab_cplus_dior_test_2026-07-14.md`

## 跨数据集 Baseline 原则

第二个数据集的 baseline 不能使用 DIOR-R 训练得到的 `best.pt` 继续训练。正确做法是每个数据集都从同一个官方预训练权重起跑：

```text
DIOR-R:
weights/pretrained/yolo11n-obb.pt -> DIOR-R baseline/A/B/C/AB/ABC

第二数据集:
weights/pretrained/yolo11n-obb.pt -> 第二数据集 baseline/A/B/C/AB/ABC
```

除非论文明确做“跨数据集迁移学习”，否则不要把 DIOR-R 的 `best.pt` 用作第二数据集的初始化权重。

## 实验矩阵

每个数据集上建议保留 1 个 baseline 和 5 个改进实验：

1. Baseline：YOLO11n-OBB。
2. 创新点 A：小目标特征增强，当前第一版采用 P2/4 OBB 检测分支。
3. 创新点 B：遥感上下文注意力，当前实现为轻量 `SPPFLSK` 大选择核上下文模块。
4. 创新点 C：旋转目标几何适应，例如轻量 DCN/DCNv3 或动态检测头。
5. 双创新点融合：优先尝试 A + B-PKI-Lite。
6. 三创新点融合：A + B + C。

如果按“改进实验”计数，两个数据集是 `5 x 2 = 10` 个实验；如果按论文表格行数计数，两个数据集都包含 baseline，则是 `6 x 2 = 12` 行。

## 结构变体管理

后续 A、B、C、AB、ABC 都会改变网络结构。为了让实验可复现、可回滚、可消融，原则上不直接反复手改原始 `yolo11-obb.yaml` 或官方模块文件。

建议后续统一整理为：

```text
ultralytics/cfg/models/11/remote_obb/
  yolo11n-obb-baseline.yaml
  yolo11n-obb-a-p2.yaml
  yolo11n-obb-b-lsk.yaml
  yolo11n-obb-b-pki-lite.yaml
  yolo11n-obb-c-dynamic.yaml
  yolo11n-obb-c-dynamic-plus.yaml
  yolo11n-obb-c-gra-lite.yaml
  yolo11n-obb-c-chol-lite.yaml
  yolo11n-obb-ab-p2-pki-lite.yaml
  yolo11n-obb-abc-p2-pki-geo-plus.yaml
  yolo11n-obb-abc-p2-pki-chol-lite.yaml

ultralytics/nn/modules/
  remote_obb_blocks.py
```

`remote_obb` 表示遥感旋转框检测，避免使用容易和 RSOD 数据集混淆的 `rsod`。所有结构变体都应从 `weights/pretrained/yolo11n-obb.pt` 起训，AB/ABC 是结构组合实验，不是权重接力实验。

实验 A 已完成训练和评估；如需复跑或迁移到服务器，可先检查配置：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --dry-run
```

正式训练时去掉 `--dry-run`。当前 A-P2 权重已整理到 `weights/experiments/dior/a_p2/best.pt`。

实验 B 已完成训练和评估，采用 `SPPFLSK` 轻量上下文注意力模块，不需要额外下载论文代码或第三方依赖。当前 test 结果未超过 baseline：

```bash
python scripts/train_obb.py --config experiments/dior/b_lsk.yaml --dry-run
```

如需复跑，正式训练时去掉 `--dry-run`。这里的 B-LSK 是旧版 B 单独创新点实验，不叠加 A-P2；由于结果未提升，暂不建议用 B-LSK 做 A+B 融合。当前 A+B 融合改用新版 B-PKI-Lite。

新版 B-PKI-Lite 已完成训练和评估，参考 CVPR 2024 PKINet，只改 top-down neck 的 P5->P4、P4->P3 融合块，不新增 P2 检测尺度，也不改 OBB 几何回归。该实验已续训到 100 epoch，但 `last_epoch100.pt` 低于 `best.pt`，最终对比建议使用 `best.pt`。本地复跑前检查命令：

```bash
python scripts/train_obb.py --config experiments/dior/b_pki_lite.yaml --env local --dry-run
```

服务器 `/home/ws` 配置使用 `batch=-1` 自动 batch，检查命令：

```bash
python scripts/train_obb.py --config experiments/dior/b_pki_lite_homews.yaml --dry-run
```

A+B-PKI-Lite 融合实验已完成代码和配置。该结构保留 A 的 P2/4 检测分支，同时只在原 top-down neck 的 P5->P4、P4->P3 融合块使用 `C3k2PKI`，不把 PKI 加到新增 P2 分支上。本地检查命令：

```bash
python scripts/train_obb.py --config experiments/dior/ab_p2_pki_lite.yaml --env local --dry-run
```

服务器 `/home/ws` 配置使用 `batch=-1` 自动 batch，训练命令：

```bash
python scripts/train_obb.py --config experiments/dior/ab_p2_pki_lite_homews.yaml
```

实验 C 已完成训练和评估，采用轻量 `C3k2Geo` 方向几何感知 head 模块，不需要下载 DCNv3/InternImage 等外部代码或编译 CUDA op。当前 test split 结果相对 baseline 的 mAP50-95 和小目标指标略有提升，但不如 A-P2 明显：

```bash
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --dry-run
```

如需复跑，正式训练时去掉 `--dry-run`。C 是单独创新点实验，不叠加 A-P2 或 B-PKI-Lite。

C-Dynamic-Plus 已完成训练和评估。该版本不覆盖原 C-Dynamic，而是在 OBB head 的 P3/P4/P5 输出融合层使用更强的 `C3k2GeoPlus`，加入通道压缩/还原、四方向分支、空间门控和通道门控。结果比原 C-Dynamic 略好，但仍属于轻微正向。本地复跑前检查命令：

```bash
python scripts/train_obb.py --config experiments/dior/c_dynamic_plus.yaml --env local --dry-run
```

服务器 `/home/ws` 配置使用 `batch=-1` 自动 batch，训练命令：

```bash
python scripts/train_obb.py --config experiments/dior/c_dynamic_plus_homews.yaml
```

当前 test 评估摘要参数量为 2,696,431，相对 baseline 增加 38,808（+1.46%）；全尺度 mAP50-95 为 0.6896，小目标 mAP50-95 为 0.3541。

C-GRA-Lite 已完成训练和评估。该版本参考 ECCV 2024 GRA 的 group-wise rotating / attention 思想，但不直接迁移其 MMDetection/MMCV 工程；当前实现为 `C3k2GRA`，在 OBB head 的 P3/P4/P5 输出融合层使用水平、垂直、主对角、反对角四个方向掩码 depthwise 分支，并通过输入自适应 routing 做方向融合。DIOR-R test 上全尺度 mAP50-95 为 0.6861，小目标 mAP50-95 为 0.3522，小目标略高于 baseline，但低于 C-Dynamic-Plus，因此暂不优先训练 A+B-PKI-Lite+C-GRA-Lite。

```bash
python scripts/train_obb.py --config experiments/dior/c_gra_lite_homews.yaml
```

如需保留或复查 A+B-PKI-Lite+C-GRA-Lite，配置仍可用：

```bash
python scripts/train_obb.py --config experiments/dior/abc_p2_pki_gra_lite_homews.yaml
```

当前评估摘要参数量：C-GRA-Lite 为 2,713,135；A+B-PKI-Lite+C-GRA-Lite 构建检查参数量为 2,885,382。本地和 `/home/ws` dry-run、预训练权重迁移、dummy forward 均正常。

C-Chol-Lite 已完成训练和评估。这个方向先显式避开 YOLO11 已有内容：本仓库的 YOLO11-OBB 已经有 ProbIoU、基于 Gaussian covariance 的 OBB 相似度、旋转 TaskAlignedAssigner、DFL 和周期角度 loss；因此 C-Chol-Lite 不再重复普通 Gaussian/ProbIoU，而是在标准 OBB head 上新增训练时 `OBBCholesky` 辅助分支，预测 3 个 Cholesky/SPD 协方差参数，并用 `chol_loss` 约束旋转框几何形状。推理时不输出 `chol`，decode/NMS 与原 YOLO11-OBB 保持一致。本地检查命令：

```bash
python scripts/train_obb.py --config experiments/dior/c_chol_lite.yaml --env local --dry-run
```

服务器 `/home/ws` 配置使用 `batch=-1` 自动 batch、`cache=ram`，训练命令：

```bash
python scripts/train_obb.py --config experiments/dior/c_chol_lite_homews.yaml
```

DIOR-R test 上 C-Chol-Lite 全尺度 mAP50-95 为 0.6902，小目标 mAP50-95 为 0.3589，已经超过 C-Dynamic-Plus，是当前最好的 C 单点。下一步建议训练 A+B-PKI-Lite+C-Chol-Lite：

```bash
python scripts/train_obb.py --config experiments/dior/abc_p2_pki_chol_lite_homews.yaml
```

当前评估摘要参数量：C-Chol-Lite 为 2,729,296；A+B-PKI-Lite+C-Chol-Lite 构建检查参数量为 2,897,906。本地和 `/home/ws` dry-run、预训练权重迁移、dummy forward、训练态 5 项 loss 检查均正常。

A+B-PKI-Lite+C-Dynamic-Plus 三创新点融合实验已完成训练和评估。该结构保留 A 的 P2/4 检测分支，B-PKI-Lite 仍只作用于原 top-down neck 的 P5->P4、P4->P3 融合块，C-Dynamic-Plus 作用于 OBB(P2/P3/P4/P5) 四个最终输出融合层。本地检查命令：

```bash
python scripts/train_obb.py --config experiments/dior/abc_p2_pki_geo_plus.yaml --env local --dry-run
```

服务器 `/home/ws` 配置使用 `batch=-1` 自动 batch、`cache=ram` 内存缓存，训练命令：

```bash
python scripts/train_obb.py --config experiments/dior/abc_p2_pki_geo_plus_homews.yaml
```

当前 test 评估摘要参数量为 2,784,390，GFLOPs 为 11.1；全尺度 mAP50-95 为 0.7149，小目标 mAP50-95 为 0.4242。该结果明显高于 baseline，但低于 A+B-PKI-Lite，因此论文主结果候选仍建议使用 A+B-PKI-Lite，ABC 作为三创新点融合消融行保留。

## 验证脚本

统一使用：

```bash
python scripts/evaluate_obb.py
```

常用命令：

```bash
python scripts/evaluate_obb.py --model weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt --data DIOR.yaml --split test --mode both
python scripts/evaluate_obb.py --model weights/experiments/dior/a_p2/best.pt --data DIOR.yaml --split test --mode both
python scripts/evaluate_obb.py --model weights/experiments/dior/b_pki_lite/best.pt --data DIOR.yaml --split test --mode both
python scripts/evaluate_obb.py --model weights/experiments/dior/c_dynamic/best.pt --data DIOR.yaml --split test --mode both
python scripts/evaluate_obb.py --model weights/experiments/dior/abc_p2_pki_geo_plus/best.pt --data DIOR.yaml --split test --mode both
python scripts/evaluate_obb.py --model path/to/best.pt --data DOTAv1.yaml --split test --mode all
python scripts/evaluate_obb.py --model path/to/best.pt --data DIOR.yaml --mode small
```

说明：

- `--mode all`：评估全尺度目标。
- `--mode small`：只评估小目标。
- `--mode both`：先评估全尺度目标，再评估小目标。
- 小目标评估依赖 `ultralytics/models/yolo/obb/val.py` 中的 `EVAL_SMALL_ONLY` 开关。
- 当前小目标定义是模型输入尺度下 `w * h < 1024`，在 `imgsz=640` 时约等价于小于 `32x32`。

## 顶会论文与代码沉淀

相关论文、官方代码入口和迁移计划放在：

```text
research/top_conference/
```

当前优先参考：

- EfficientDet / BiFPN：用于小目标多尺度特征融合。
- LSKNet：用于遥感场景长程上下文和大选择核注意力。
- InternImage / DCNv3：用于动态空间采样和旋转目标几何适应。
- Dynamic Head：作为检测头注意力的备选方向。

这些论文负责提供动机和模块设计依据；实际实现时要以 YOLO11n-OBB 的轻量化、可复现和消融清晰为第一优先级。当前 B-LSK 为 LSKNet 思想的轻量适配实现，C-Dynamic 为方向几何感知的轻量适配实现，均未直接复制第三方仓库代码。

## 项目备注

本仓库已按遥感 OBB 实验用途裁剪，删除了官方 `docs/`、`examples/`、`docker/`、`.github/`、`tests/` 等通用工程文件。官方 Ultralytics 用法需要时直接查在线文档。

更详细的实验约定、脚本状态和后续开发注意事项见：

```text
AGENTS.md
```

本地 Codex 改代码、Git 同步到服务器训练、后续 `git pull` 更新服务器代码的完整流程见：

```text
SERVER_TRAINING.md
```

如果服务器没有 conda，使用 Python `venv` 部署，见：

```text
SERVER_VENV_SETUP.md
```

本地运行：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env local --dry-run
```

服务器运行：

```bash
git pull
python scripts/train_obb.py --config experiments/dior/c_dynamic.yaml --env homews --dry-run
```

公司 5090 服务器可使用：

```bash
python scripts/train_obb.py --config experiments/dior/a_p2.yaml --env company5090 --dry-run
```

服务器训练完成后，把关键 `best.pt/last.pt` 整理到 `weights/experiments/<dataset>/<variant>/`，可以直接 `git add`、`git commit`、`git push` 回传；本地再 `git pull` 获取权重。

服务器自检脚本：

```bash
python scripts/check_server_env.py --env homews --require-cuda
```

官方 Ultralytics 文档请参考：https://docs.ultralytics.com/
