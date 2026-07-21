# YOLO11n-OBB 遥感小目标检测实验仓库

本仓库基于 Ultralytics YOLO 源码，用于完成一篇面向 EI 会议的论文，并服务后续毕业学位论文。研究对象是遥感影像小目标的 OBB 旋转框检测。当前主线任务是以 YOLO11n-OBB 为基础模型，在 DIOR-R 和第二个遥感 OBB 数据集上完成 baseline、三个创新点和融合消融实验。

## 研究目标

- 任务：遥感图像小目标检测，采用 OBB 旋转框检测形式。
- 论文定位：EI 会议论文 + 毕业学位论文。
- 基础模型：`weights/pretrained/yolo11n-obb.pt`。
- 主数据集：DIOR-R。
- 第二数据集：HRSID。seed3407 已完成 baseline/A/B/AB 四组，并实现四项一致的 `AB > A > B > baseline`；UCAS-AOD、VEDAI、SSDD-RBox、HRSC2016 保留为筛选记录。
- 论文实验目标：设计 3 个轻量、可解释、可消融的模型改进点，并验证单独改进和组合改进的效果。

## 论文主实验：DIOR-R 官方划分

EI 小论文的第一个数据集现统一采用 DIOR 官方 `5862/5863/11738` train/val/test 划分。baseline、A-P2、B-PKI-Lite 和 A+B-PKI-Lite 四组已经完成，AB 在全尺度和小目标四项指标上均为最高。

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 2,657,623 | 6.6 | 0.7111 | 0.5431 | 0.2732 | 0.1796 |
| A-P2 | 2,698,340 | 10.5 | 0.7160 | 0.5394 | 0.2843 | 0.1980 |
| B-PKI-Lite | 2,699,673 | 6.8 | 0.7111 | 0.5424 | 0.2768 | 0.1823 |
| A+B-PKI-Lite | **2,740,390** | **10.7** | **0.7225** | **0.5455** | **0.2920** | **0.2042** |

DIOR-R 论文传统上多以全数据集 AP50 为主要指标，本项目也以全尺度 mAP50 作为主报告指标，同时保留 mAP50-95 作为更严格的补充指标。外部方法的 AP50 只能放入标注 `Reported under authors' settings` 的参考表：本项目与 MMRotate 工作在 train/trainval、48 张 test 过滤以及 ProbIoU/几何旋转 IoU 上仍有差异，不能据此宣称严格领先。小目标结果使用本项目 `640×640` 输入空间内 OBB 面积 `<1024 px²` 的附加协议，不等同于 DIOR-R 官方指标。

官方划分数据、配置和完整结果见 `experiments/dior_official/`。YOLOv8n-OBB 与 YOLO26n-OBB 的同协议复现配置位于 `experiments/dior_official/comparisons/`，本地和 `/home/ws` 均可直接训练。原 `18770/2346/2347` 的 8:1:1 四组结果不再作为论文第一数据集主表，改作不同数据划分下的附加鲁棒性验证。

## 历史 8:1:1 鲁棒性验证 Baseline

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

## 历史 8:1:1 鲁棒性验证结果

以下结果使用第三方 YOLODIOR-R 的 `18770/2346/2347` 划分，现定位为不同数据划分下的附加鲁棒性验证和学位论文探索记录，不再替代官方划分主表。A-P2、B-LSK、C-Dynamic、C-Dynamic-Plus、C-GRA-Lite、C-Chol-Lite、B-PKI-Lite、A+B-PKI-Lite、A+B-PKI-Lite+C-Plus 和 A+B-PKI-Lite+C-Chol-Lite 已完成 `test` split 评估；其中 A+B-PKI-Lite 仍是该划分的最佳主线组合。

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
| C-SET-HBS（待训练） | 待训练 | 约 2,706,311 | baseline 推理路径 | - | - | - | - |
| A+B-PKI-Lite | `weights/experiments/dior/ab_p2_pki_lite/best.pt` | 2,740,390 | 10.7 | 0.8859 | 0.7198 | 0.5958 | 0.4288 |
| A+B-PKI-Lite+C-Plus | `weights/experiments/dior/abc_p2_pki_geo_plus/best.pt` | 2,784,390 | 11.1 | 0.8832 | 0.7149 | 0.5838 | 0.4242 |
| A+B-PKI-Lite+C-Chol-Lite | `weights/experiments/dior/abc_p2_pki_chol_lite/best.pt` | 2,819,058 | 10.7 | 0.8862 | 0.7190 | 0.5774 | 0.4209 |
| A+B-PKI-Lite+C-SET-HBS（待训练） | 待训练 | 约 2,789,758 | 与 AB 推理路径相同 | - | - | - | - |
| A-P2 相对 baseline | - | +40,717 | +3.9 | +0.0191 | +0.0116 | +0.0684 | +0.0745 |
| B-LSK 相对 baseline | - | +118,471 | +0.1 | -0.0008 | -0.0065 | -0.0076 | -0.0032 |
| B-PKI-Lite 相对 baseline | - | +42,050 | +0.2 | +0.0000 | +0.0011 | +0.0103 | +0.0151 |
| C-Dynamic 相对 baseline | - | +19,317 | +0.0 | -0.0026 | +0.0010 | +0.0027 | +0.0057 |
| C-Dynamic-Plus 相对 baseline | - | +38,808 | +0.1 | +0.0000 | +0.0022 | +0.0122 | +0.0071 |
| C-GRA-Lite 相对 baseline | - | +55,512 | +0.1 | -0.0005 | -0.0013 | +0.0073 | +0.0052 |
| C-Chol-Lite 相对 baseline | - | +71,673 | +0.0 | -0.0011 | +0.0028 | +0.0136 | +0.0119 |
| A+B-PKI-Lite 相对 baseline | - | +82,767 | +4.1 | +0.0271 | +0.0324 | +0.0812 | +0.0818 |
| A+B-PKI-Lite+C-Plus 相对 baseline | - | +126,767 | +4.5 | +0.0244 | +0.0275 | +0.0692 | +0.0772 |
| A+B-PKI-Lite+C-Chol-Lite 相对 baseline | - | +161,435 | +4.1 | +0.0274 | +0.0316 | +0.0628 | +0.0739 |

轻量化对比：A-P2、B-PKI-Lite、C-Dynamic、C-Dynamic-Plus、C-GRA-Lite、C-Chol-Lite 相对 baseline 的参数增幅分别为 +1.53%、+1.58%、+0.73%、+1.46%、+2.09%、+2.70%；A+B-PKI-Lite 的评估摘要参数量为 2,740,390，相对 baseline 增加 82,767，增幅 +3.11%；A+B-PKI-Lite+C-Plus 的评估摘要参数量为 2,784,390，相对 baseline 增加 126,767，增幅 +4.77%；A+B-PKI-Lite+C-Chol-Lite 的评估摘要参数量为 2,819,058，相对 baseline 增加 161,435，增幅 +6.07%。

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
- `weights/experiments/dior/abc_p2_pki_chol_lite/eval_dior_test_2026-07-16.md`
- `weights/experiments/dior/abc_p2_pki_chol_lite/compare_with_baseline_ab_cplus_dior_test_2026-07-16.md`

## 跨数据集 Baseline 原则

第二个数据集的 baseline 不能使用 DIOR-R 训练得到的 `best.pt` 继续训练。正确做法是每个数据集都从同一个官方预训练权重起跑：

```text
DIOR-R:
weights/pretrained/yolo11n-obb.pt -> DIOR-R baseline/A/B/C/AB/ABC

第二数据集:
weights/pretrained/yolo11n-obb.pt -> 第二数据集 baseline/A/B/C/AB/ABC
```

除非论文明确做“跨数据集迁移学习”，否则不要把 DIOR-R 的 `best.pt` 用作第二数据集的初始化权重。

UCAS-AOD 本地数据位于 `C:/E/datasets/UCAS-AOD-YOLO/`，服务器约定放在 `/home/ws/datasets/UCAS-AOD-YOLO/`。数据集与四组消融训练命令见 `experiments/ucas_aod/README.md`。

UCAS-AOD 四组自动 batch 和固定 `batch=32` 复核均已完成。固定 batch 下，B-PKI-Lite 的小目标 mAP50-95 由 baseline 的 0.7371 提升到 0.7410，但全尺度 mAP50-95 从 0.8024 降至 0.8006；A-P2 和 A+B-PKI-Lite 仍未超过 baseline。完整记录见 `weights/experiments/ucas_aod/eval_ucas_aod_test_batch32_2026-07-17.md`。

由于 UCAS-AOD 不支持 A/AB 的跨数据集增益，已新增 VEDAI-1024 作为轻量微小目标 OBB 筛选数据集。官方数据转换脚本为 `scripts/convert_vedai_to_yolo_obb.py`，固定使用官方 fold10 test、fold02 val、其余八个 fold train；转换与四组训练命令见 `experiments/vedai/README.md`。

VEDAI-1024 四组固定 `batch=32` 筛选已完成。B-PKI-Lite 在 fold10 test 上的全尺度/小目标 mAP50-95 为 0.5756/0.5365，高于 baseline 的 0.5661/0.5293；A-P2 和 AB 均明显低于 baseline。因此 VEDAI 可作为 B 的辅助证据，但不适合作为当前 AB 主方法的第二数据集主结果。完整记录见 `weights/experiments/vedai/eval_vedai_fold10_test_2026-07-17.md`。

为保留 A-P2 与 B-PKI-Lite 的方法主线，新增的 VEDAI 专用 A-P2-Plus 已完成训练。它保留 P2/4 检测尺度，加宽、加深 P2 融合，并加入低频语义守门。fold10 test 小目标 mAP50/mAP50-95 为 0.7054/0.5444，相对 baseline 提升 `+0.0223/+0.0151`，也高于 B；全尺度 mAP50-95 为 0.5507，仍低于 baseline 0.5661。当前 B 全尺度最佳、A-P2-Plus 小目标最佳，具备继续做 AB-Plus 的互补依据。

VEDAI AB-Plus 已完成训练和评估。它使用 A-Plus 的 P2 语义守门，并只在 P5→P4、P4→P3 两个原 top-down 融合块使用 B-PKI-Lite。fold10 test 全尺度/小目标 mAP50-95 为 0.5263/0.4955，仍低于 baseline 的 0.5661/0.5293。AB-Plus 比旧 AB 明显改善，但当前串联方式下 B 冲淡了 A-Plus 的误检抑制，未实现预期互补。

针对串联干扰新增的 VEDAI AB-Plus-Decoupled 已完成训练和评估。它完整保留 A-P2-Plus 主路，B-PKI-Lite 使用独立 top-down 辅助路径，并通过零初始化逐通道残差门只在最终 P3/P4 特征注入。fold10 test 四项为 0.7336/0.5487/0.6768/0.5222，比串联 AB-Plus 明显恢复，但只有全尺度 mAP50 超过 baseline，尚未达到 AB 成功标准。

结构更直接的 VEDAI AB-PKI-Heavy 也已完成训练和评估。它使用单路径，P2Guard 之前保持普通融合，将 B-PKI 后移到最终 P3/P4 层，并同时增加 P2/P3/P4 通道和深度。fold10 test 四项为 0.7334/0.5431/0.6775/0.5208，与解耦版接近但未更好，说明继续简单增加容量不能解决 VEDAI 上的 AB 组合问题。

为保持 DIOR-R 原版 A/B/AB 结构不变，VEDAI 又完成了统一 `imgsz=512` 的四组复核。baseline 四项为 0.6720/0.4643/0.6351/0.4268；A 为 0.5695/0.4240/0.5161/0.3730；B 为 0.6756/0.4541/0.6362/0.4156；AB 为 0.5736/0.4140/0.5314/0.3685。B 仅两个 mAP50 极小幅上升，而两个 mAP50-95 下降；A 和 AB 明显负向。降低输入分辨率未解决 P2 分支问题，该组作为失败复核保留，不进入论文主表。

下一套轻量第二数据集已确定为 Official SSDD 的 RBox-SSDD。官方发布包位于 `C:/E/datasets/Official-SSDD-OPEN/`，转换后的 YOLO-OBB 数据位于 `C:/E/datasets/SSDD-RBox-YOLO/`。发布包实际含 1160 张 SAR 图和 2587 个旋转船舶框；保留官方 232 张 test，从官方 train 固定划分后得到 835 train、93 val。Ultralytics OBB 已完整扫描，0 缺失、0 背景、0 损坏。baseline/A/B/AB 的本地和 `/home/ws` 配置位于 `experiments/ssdd_rbox/`，筛选与转换说明见 `research/datasets/SECOND_DATASET_SELECTION.md`。

SSDD-RBox 已完成 seed=42 和 seed=2024 两套完整四组消融，并预筛选 seed=3407、seed=0。seed=42 下 A、B 单点正向但 AB 不是最优；seed=2024 下 AB 的全尺度/小目标 mAP50-95 为 0.7954/0.6999，均高于同 seed baseline 的 0.7938/0.6926，但 A、B 单点退化；seed=3407 的 AB 小目标略低于同 seed baseline，seed=0 的 AB 明显退化。因此目前没有一套 SSDD seed 同时满足 A、B、AB 均正向且 AB 最优，不能跨 seed 拼接最终消融表。完整记录见 `weights/experiments/ssdd_rbox/eval_ssdd_rbox_test_2026-07-18.md`。

HRSC2016 已完成官方发布包解压和 YOLO-OBB 转换。原始目录为 `C:/E/datasets/HRSC2016/HRSC2016/`，转换输出为 `C:/E/datasets/HRSC2016-YOLO/`；严格采用压缩包 `ImageSets` 的 436/181/453 train/val/test 划分，共 1207/541/1228 个 OBB，Ultralytics 扫描 0 损坏。`imgsz=640` 下 test 仅 61 个小目标，因此该数据集优先用于快速筛选全尺度泛化，小目标结果需谨慎解释。转换脚本和实验配置分别位于 `scripts/convert_hrsc2016_to_yolo_obb.py`、`experiments/hrsc2016/`。

HRSC2016 的 baseline 与 AB 筛选已完成。baseline test 四项为 `0.9584/0.8289/0.3665/0.2852`，AB 为 `0.9530/0.7900/0.3498/0.2805`，AB 全部下降，因此按预设停止条件不再补 A/B 或换 seed。记录见 `weights/experiments/hrsc2016/eval_hrsc2016_test_2026-07-19.md`。

随后从官方 HRSID 仓库下载 JPG 数据并转换为 YOLO-OBB。保留官方 1962 张 test，从官方 train 分层划出 val，最终为 3278/364/1962 张图和 9974/1064/5918 个 OBB；test 有 5350 个小目标，适合检验 P2 分支。转换脚本、数据配置和训练配置位于 `scripts/convert_hrsid_to_yolo_obb.py`、`ultralytics/cfg/datasets/HRSID.yaml`、`experiments/hrsid/`。

HRSID seed3407 完整四组 test 四项为：baseline `0.7513/0.3963/0.7160/0.3736`、A `0.9371/0.6706/0.9178/0.6610`、B `0.7620/0.4191/0.7273/0.3888`、AB `0.9396/0.6765/0.9212/0.6687`，顺序为全尺度 mAP50/mAP50-95、小目标 mAP50/mAP50-95。四项均满足 `AB > A > B > baseline`；该 seed 的完整四行作为论文第二数据集主表，不与 seed42/2024 拼接。完整记录见 `weights/experiments/hrsid/eval_hrsid_test_2026-07-19.md`。

VEDAI 主消融继续遵守与 DIOR-R 相同的公平协议：baseline、A、B、AB 必须全部从 `weights/pretrained/yolo11n-obb.pt` 独立起训，并使用相同 split、batch、epochs、seed、训练超参和评估协议。AB 不得从 A/B `best.pt` 续训，不得冻结 A 后只训 B，不得增加独有训练阶段。所有已完成的 VEDAI 配置已复核，均使用统一通用预训练权重。

## 实验矩阵

每个数据集上建议保留 1 个 baseline 和 5 个改进实验：

1. Baseline：YOLO11n-OBB。
2. 创新点 A：小目标特征增强，当前第一版采用 P2/4 OBB 检测分支。
3. 创新点 B：neck 特征融合增强，当前主线为轻量 `C3k2PKI` / B-PKI-Lite；旧 `SPPFLSK` 仅保留为负向探索。
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
  yolo11n-obb-abc-p2-pki-set-hbs.yaml

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

DIOR-R test 上 C-Chol-Lite 全尺度 mAP50-95 为 0.6902，小目标 mAP50-95 为 0.3589，已经超过 C-Dynamic-Plus，是当前最好的 C 单点。A+B-PKI-Lite+C-Chol-Lite 组合也已完成训练和评估：

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

A+B-PKI-Lite+C-Chol-Lite 三创新点融合实验已完成训练和评估。该结构保留 A 的 P2/4 检测分支，B-PKI-Lite 仍只作用于原 top-down neck 的 P5->P4、P4->P3 融合块，C-Chol-Lite 在 OBB head 上新增训练时 Cholesky/SPD 协方差辅助分支；推理和评估时仍使用标准 OBB 输出。本地/服务器配置仍保留：

```bash
python scripts/train_obb.py --config experiments/dior/abc_p2_pki_chol_lite.yaml --env local --dry-run
python scripts/train_obb.py --config experiments/dior/abc_p2_pki_chol_lite_homews.yaml
```

本次实际训练为 AutoDL 双 RTX 3090 续训，训练期 best 出现在 epoch 100。当前 test 评估摘要参数量为 2,819,058，GFLOPs 为 10.7；全尺度 mAP50 为 0.8862，全尺度 mAP50-95 为 0.7190，小目标 mAP50-95 为 0.4209。该结果明显高于 baseline，且全尺度 mAP50 略高于 A+B-PKI-Lite，但 mAP50-95 和小目标指标仍低于 A+B-PKI-Lite，因此主结果候选仍建议使用 A+B-PKI-Lite，ABC-Chol 作为三创新点融合消融行保留。

A+B-PKI-Lite+C-SET-HBS 是下一组优先 ABC 实验，参考 CVPR 2025 SET 的 HBS 思路，但只实现贡献最大且训练稳定的 HBS 部分，不声称复现完整 SET。C 根据旋转 GT 生成前景掩码，保留前景特征，只对背景做尺度相关平滑，并通过共享 OBB head 形成训练辅助监督；验证和推理仍完全使用原 AB 主路径。论文和实现说明见 `research/top_conference/set_2025/`。

为了保证最终消融表中 C 与 ABC 使用同一个创新点，单独 C-SET-HBS 配置也已准备：

```bash
python scripts/train_obb.py --config experiments/dior/c_set_hbs.yaml --env local
python scripts/train_obb.py --config experiments/dior/c_set_hbs_homews.yaml
```

单独 C 可以在 ABC 超过 AB 后再补训；若按标准消融顺序，也可以先训练 C 再训练 ABC。

本地检查与训练：

```bash
python scripts/train_obb.py --config experiments/dior/abc_p2_pki_set_hbs.yaml --env local --dry-run
python scripts/train_obb.py --config experiments/dior/abc_p2_pki_set_hbs.yaml --env local
```

`/home/ws` 一键训练使用约定的 `batch=-1` 和 `cache=ram`：

```bash
python scripts/train_obb.py --config experiments/dior/abc_p2_pki_set_hbs_homews.yaml
```

DIOR `nc=20` 构建参数求和为 2,797,774，其中 HBS 只比 AB 增加 49,368；按现有 Ultralytics 评估摘要口径预计约为 2,789,758，相对 baseline 约增加 4.97%。HBS 不参与推理，因此推理 GFLOPs 和输出协议与 AB 相同。已通过本地/服务器 dry-run、297/793 项预训练权重迁移、训练态 5 项 loss、反向梯度和 eval 输出检查。

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
python scripts/evaluate_obb.py --model weights/experiments/dior/abc_p2_pki_chol_lite/best.pt --data DIOR.yaml --split test --mode both
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
