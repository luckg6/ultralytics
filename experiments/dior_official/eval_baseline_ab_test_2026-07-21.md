# DIOR-R 官方划分四组消融评估

评估日期：2026-07-21

> 整理说明：本文件保留 DIOR-R official 首轮四组 test 评估原始记录。当前论文已经补充三 seed 稳定性，最终报告口径以 `paper/ippr2026/main.pdf`、`README.md` 和 `experiments/dior_official/README.md` 为准。本文件中的 seed42/自动 batch 说明不再作为复现论文表格的完整协议。

## 实验对象

| 模型 | 权重 |
|---|---|
| YOLO11n-OBB baseline | `runs/obb/dior_official_baseline_yolo11n_obb2/weights/best.pt` |
| A-P2 | `runs/obb/dior_official_A_p2/weights/best.pt` |
| B-PKI-Lite | `runs/obb/dior_official_B_pki_lite/weights/best.pt` |
| A-P2 + B-PKI-Lite | `runs/obb/dior_official_AB_p2_pki_lite/weights/best.pt` |

四组均从 `weights/pretrained/yolo11n-obb.pt` 初始化，使用 `epochs=100`、`imgsz=640`、`seed=42`、`deterministic=True`、`cache=ram` 和自动 batch。训练 GPU 编号不同，但均为同一服务器环境中的独立单卡训练。

## 官方 test 结果

评估命令统一使用 `scripts/evaluate_obb.py`、`split=test`、`mode=both` 和 `imgsz=640`。

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| baseline | 0.7111 | 0.5431 | 0.2732 | 0.1796 |
| A-P2 | 0.7160 | 0.5394 | 0.2843 | 0.1980 |
| B-PKI-Lite | 0.7111 | 0.5424 | 0.2768 | 0.1823 |
| A-P2 + B-PKI-Lite | **0.7225** | **0.5455** | **0.2920** | **0.2042** |

### 相对 baseline 的变化

| 模型 | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|
| A-P2 | +0.0049 | -0.0037 | +0.0111 | +0.0184 |
| B-PKI-Lite | +0.0000 | -0.0007 | +0.0036 | +0.0027 |
| A+B | **+0.0114** | **+0.0024** | **+0.0188** | **+0.0246** |

A、B 单独使用时都提升了两项小目标指标，但全尺度 mAP50-95 略低于 baseline。AB 则在四项 test 指标上均超过 baseline、A 和 B，其中小目标 mAP50-95 相对 baseline 提升 2.46 个百分点。

AB 相对 A 的四项提升为 +0.0065/+0.0061/+0.0077/+0.0062，相对 B 为 +0.0114/+0.0031/+0.0152/+0.0219。组合结果没有落入单模块之间，而是四项均进一步提升，支持 A 的 P2 小目标分支与 B 的 neck 多核上下文融合具有正向互补性。

## 训练期 val 补充

| 模型 | 最佳 epoch | 最佳 val mAP50 | 最佳 val mAP50-95 |
|---|---:|---:|---:|
| baseline | 90 | 0.79741 | 0.63740 |
| A-P2 | 100 | 0.80242 | 0.62735 |
| B-PKI-Lite | 87 | 0.79715 | 0.63763 |
| A-P2 + B-PKI-Lite | 87 | 0.80343 | 0.63489 |

AB 的 val mAP50 最高，但 val mAP50-95 不是最高；最终官方 test 上 AB 四项最优。论文中应报告 test 主结果，不应把 val 和 test 的优势混写。

## 数据质量说明

现有 Kaggle YOLO-OBB 转换标签中共有 140 张图像含越界顶点：官方 train/val/test 分别为 62/30/48 张。Ultralytics 会将这些图像整张忽略，因此当前实际参与扫描的有效图像数为 5,800/5,833/11,690。

- 140 张图像中共有 166 个越界实例，坐标范围最低为 -0.29、最高为 1.3175。
- 其中 67 张图像还包含 609 个原本有效的实例，但也随整图一起被忽略。
- baseline 与 AB 使用完全相同的数据处理，因此本次内部消融比较仍然公平。
- 用户已决定保留该统一过滤规则，不重新训练四组。若用于和采用原始 DIOR-R 标注解析器的论文直接横向比较，必须披露该预处理差异。

## 当前结论

四组消融已完成。A-P2 和 B-PKI-Lite 单独使用时均改善小目标检测，AB 在全尺度和小目标四项指标上均取得最高结果，并超过两个单模块，符合论文所需的组合互补证据。越界标签按统一过滤规则保留，不再安排清理后的重复训练。

## 小目标指标解释

官方 test 的有效标签中约 85,045 个实例满足输入空间 OBB 面积 `<1024 px²`，约占全部有效实例的 68.6%。因此全尺度 mAP 较高不能简单解释成“大目标在数量上把结果拉高”。

主要原因是：小目标像素信息少、定位误差对 IoU 更敏感；全尺度评估还包含同类别中更容易的中大目标；mAP 是类别宏平均而不是按实例数加权。小目标子集中 airport 仅 3 个、trainstation 仅 1 个，basketballcourt/chimney/dam 等类别也只有几十到一百余个实例，这些类别的零或低 AP 会明显压低小目标宏平均。

该小目标评估还会同时保留面积 `<1024 px²` 的 GT 与预测，属于本项目诊断协议，不是 DIOR-R 官方提供的 APs。ReDiffDet 所称的 DIOR-R “small size objects”表主要选取若干小尺寸类别，并不等同于本项目逐实例面积过滤，因此二者不可直接横向比较。

## 论文指标口径

DIOR-R 相关工作中，以全数据集 AP50 作为主要结果非常常见：OrientedFormer 的官方结果表明确列 DIOR-R `AP_50`，ReDiffDet 的 DIOR-R 主表也明确使用 AP50；PKINet 的 DIOR-R 表沿用单列 mAP 的传统写法。本文将全尺度 mAP50 作为主报告指标，同时报告全尺度 mAP50-95 作为更严格补充，并把两项小目标指标放入消融或附加分析。

外部论文 AP50 只能在 `Reported under authors' settings` 表中作参考并列，不能视为严格同协议：本项目使用 train 训练并以 val 选权重，不少论文使用 trainval；本项目过滤 48 张越界 test 图像；本仓库 OBB validator 使用 `batch_probiou` 匹配，而 MMRotate 系方法通常采用几何旋转 IoU。

论文主实验采用本目录的官方划分四组结果。旧 `18770/2346/2347` 四组结果改作不同数据划分下的附加鲁棒性验证，不与官方划分主表混合计算或排名。
