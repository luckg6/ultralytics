# 近期方法对比检索记录

> 检索日期：2026-07-20  
> 用途：为 IPPR 2026 小论文的 Related Work 与近期方法对比表提供可核验数字。  
> 原则：只记录论文原文、出版社页面或官方代码仓库中的结果；“可引用”不等于“可无条件直接比较”。

## 1. 当前结论

- **HRSID 可以建立谨慎的外部方法对比表。** 近期 YOSDet 与本项目都从 HRSID 实例掩码拟合最小面积旋转框，并使用官方 1962 张 test，指标也覆盖 AP50 和 AP50-95。
- **当前 DIOR-R 结果不能与主流论文数值作严格横向比较。** 本项目使用的第三方 YOLODIOR-R 为 18,770/2,346/2,347 的约 80/10/10 划分；主流 DIOR-R 论文通常使用 5,862 train、5,863 val、11,738 test 的官方划分。测试集不同是本项目 88.59% 与公开论文约 65%--74% AP50 差异巨大的主要原因之一。
- 因此，论文可在 DIOR-R 上保留同协议 baseline/A/B/AB 消融，但不得把公开方法的官方划分结果与本项目结果混在同一列后宣称领先。若需要严格的 DIOR-R SOTA 对比，必须补跑官方划分。

## 2. DIOR-R：可引用但不可与当前结果直接比较

以下均为论文或官方仓库报告的 DIOR-R AP50，适合用于 Related Work、说明领域进展或放入明确标注“官方划分报告值”的独立表格。

| 方法 | 年份/来源 | Backbone/设定 | DIOR-R AP50 (%) | 使用建议 |
|---|---|---|---:|---|
| PKINet-S | CVPR 2024 | Oriented R-CNN，ImageNet-1K 预训练 | 67.03 | 可直接引用；同时是 B-PKI-Lite 的主要思想来源 |
| OrientedFormer | TGRS 2024 | ResNet-50，12 epochs | 67.28 | 可直接引用 |
| ReDiffDet | CVPR 2025 | ReResNet-50 | 68.05 | 可直接引用 |
| OpenRSD | ICCV 2025 | RTMDet-L，open-prompt/multi-stage | 73.7 | 任务范式更强，只宜单列，不作为同规模轻量模型的公平对手 |

来源：

- PKINet：Cai et al., *Poly Kernel Inception Network for Remote Sensing Detection*, CVPR 2024，Table 6。[CVF 论文页面](https://openaccess.thecvf.com/content/CVPR2024/html/Cai_Poly_Kernel_Inception_Network_for_Remote_Sensing_Detection_CVPR_2024_paper.html)
- OrientedFormer：Zhao et al., *OrientedFormer: An End-to-End Transformer-Based Oriented Object Detector in Remote Sensing Images*, IEEE TGRS 2024，DOI `10.1109/TGRS.2024.3456240`。[官方代码与模型表](https://github.com/wokaikaixinxin/OrientedFormer)
- ReDiffDet：Zhao et al., *ReDiffDet: Rotation-equivariant Diffusion Model for Oriented Object Detection*, CVPR 2025，Table 3。[CVF 论文页面](https://openaccess.thecvf.com/content/CVPR2025/html/Zhao_ReDiffDet_Rotation-equivariant_Diffusion_Model_for_Oriented_Object_Detection_CVPR_2025_paper.html)
- OpenRSD：Huang et al., *OpenRSD: Towards Open-prompts for Object Detection in Remote Sensing Images*, ICCV 2025。[CVF 论文页面](https://openaccess.thecvf.com/content/ICCV2025/html/Huang_OpenRSD_Towards_Open-prompts_for_Object_Detection_in_Remote_Sensing_Images_ICCV_2025_paper.html)

DIOR-R 官方划分核对来源：AOPG 发布的 DIOR-R 沿用 DIOR 划分；近期论文也明确列出 5,862/5,863/11,738。[AOPG/DIOR-R 论文](https://arxiv.org/abs/2110.01931)，[划分说明示例](https://www.mdpi.com/2072-4292/18/5/839)

## 3. HRSID：优先采用的近期对比

### 3.1 最接近本项目协议的 YOSDet

YOSDet 明确说明：从 HRSID 原生实例分割掩码拟合 minimum-area rotated bounding box，使用 3,642 train / 1,962 test，并训练 300 epochs。其标签生成方式和 test 集与本项目最接近。

| 方法 | Params (M) | GFLOPs | AP50 (%) | AP50-95 (%) | 来源 |
|---|---:|---:|---:|---:|---|
| YOLOv11-OBB（YOSDet 论文复测） | 2.65 | 10.20 | 86.3 | 46.9 | YOSDet Table 3 / Table 5 |
| YOLOv13-OBB（YOSDet 论文复测） | 2.52 | 10.00 | 86.8 | 未报告 | YOSDet Table 3 |
| YOSDet | 2.15 | 12.30 | 88.5 | 49.1 | YOSDet Table 3 / Table 5 |
| 本项目 A+B-PKI-Lite | 2.738 | 10.7 | **93.96** | **67.65** | 本项目 test 评估 |

来源：YOSDet, *A YOLO-Based Oriented Ship Detector in SAR Imagery*, Remote Sensing 2026, 18(4), 645，DOI `10.3390/rs18040645`。[论文全文](https://www.mdpi.com/2072-4292/18/4/645)

使用限制：YOSDet 使用完整 3,642 张训练图并训练 300 epochs；本项目从官方训练集留出 364 张 val，实际训练 3,278 张，训练 100 epochs、`imgsz=640`。虽然 test 和 OBB 生成逻辑接近，正文表注仍需写“reported results under authors' settings”，不能写成完全同训练协议复现。

### 3.2 可作为补充的 2025 年 OBB 结果

| 方法 | 来源 | HRSID 指标 | 协议差异与用途 |
|---|---|---:|---|
| TIAR-SAR | Remote Sensing 2025 | AP50 88.6 | 从实例标注生成最小外接旋转框；论文使用 3,623/1,955，有少量样本差异；适合补充引用 |
| CLAFANet | Remote Sensing 2025 | AP50 83.8，AP50-95 47.6 | 随机 4:1 划分，不与本项目直接排名 |
| Weakly supervised OBB method | Remote Sensing 2025 | AP50 82.508 | 使用 65%/35% 与 800 输入，但属于水平框弱监督；适合在 Related Work 单列 |
| R-SABMNet | Remote Sensing 2025 | AP 90.69 | 明确为旋转检测，但论文表中 AP 口径及划分披露不够完整；不进入主比较表 |

来源：

- TIAR-SAR：Gu et al., *TIAR-SAR: An Oriented SAR Ship Detector Combining a Task Interaction Head Architecture with Composite Angle Regression*, Remote Sensing 2025, 17(12), 2049，DOI `10.3390/rs17122049`。[论文全文](https://www.mdpi.com/2072-4292/17/12/2049)
- CLAFANet：*Cross-Level Adaptive Feature Aggregation Network for Arbitrary-Oriented SAR Ship Detection*, Remote Sensing 2025, 17(10), 1770，DOI `10.3390/rs17101770`。[论文全文](https://www.mdpi.com/2072-4292/17/10/1770)
- 弱监督 OBB：*Weakly Supervised SAR Ship Oriented-Detection Algorithm Based on Pseudo-Label Generation Optimization and Guidance*, Remote Sensing 2025, 17(22), 3663，DOI `10.3390/rs17223663`。[论文全文](https://www.mdpi.com/2072-4292/17/22/3663)
- R-SABMNet：Li et al., *R-SABMNet: A YOLOv8-Based Model for Oriented SAR Ship Detection with Spatial Adaptive Aggregation*, Remote Sensing 2025, 17(3), 551，DOI `10.3390/rs17030551`。[论文全文](https://www.mdpi.com/2072-4292/17/3/551)

## 4. 推荐写入论文的方式

1. 主消融表继续只放本项目 baseline、A、B、AB，保证训练协议严格一致。
2. HRSID 可另设一张紧凑的“Comparison with recent OBB detectors”表，优先放 YOSDet 论文复测的 YOLOv11-OBB、YOLOv13-OBB、YOSDet 与本项目 AB。
3. 表下注明：外部结果取自原论文，训练 epoch、输入尺度和 val 使用方式不同；所有方法共享官方 HRSID test 与基于实例掩码的 OBB 生成原则。
4. DIOR-R 公开论文的官方划分数字只用于 Related Work；主对比表改为选取参数量接近的开源 OBB 模型，在本项目 80/10/10 划分上统一重训和测试。
5. 外部模型完成同划分重训前不写 `state-of-the-art`；完成后也应使用“在统一实验协议下取得更优结果”这一限定表述。

## 5. 仍需定稿前核验

- 从 YOSDet PDF 原版再次确认 HRSID 的实际训练输入尺寸；HTML 数学转码丢失了该数值。
- 确认 YOSDet Table 5 的 AP50-95 与 Table 3 的最终 YOSDet checkpoint 完全对应。
- 生成最终 BibTeX 后逐条核验作者顺序、卷期、页码和 DOI。
- DIOR-R 主对比表待补 YOLOv8n-OBB 与 YOLO26n-OBB 的同划分重训结果；训练配置和口径见 `experiments/dior/comparisons/README.md`。

## 6. DIOR-R 同划分轻量模型复现计划

为避免官方 DIOR-R 划分与本项目划分不一致带来的不可比性，不直接使用其他论文的 DIOR-R checkpoint。入选模型从各自官方通用 OBB 预训练权重出发，在本项目相同的 train/val/test、100 epochs、640 输入、seed=42 和确定性设置下重新训练。

| 方法 | 年份 | DIOR-R 20 类 Params | 640 GFLOPs | 与本文 AB 参数量差异 | 状态 |
|---|---:|---:|---:|---:|---|
| YOLOv8n-OBB | 2023 | 3,086,415 | 8.46 | +12.63% | 配置 ready，待训练 |
| YOLO26n-OBB | 2026 | 2,654,934 | 6.31 | -3.12% | 配置 ready，待训练 |
| A-P2 + B-PKI-Lite | 本文 | 2,740,390 | 10.7 | 0 | 已完成 |

YOLOv8n-OBB 用作经典 nano OBB 参照，YOLO26n-OBB 用作近期 nano OBB 参照。YOLO12n-OBB 不进入主表，因为官方未提供 OBB 预训练权重；无可核验官方源码的方法也不按论文描述自行复刻。训练完成后统一报告全尺度与小目标的 mAP50、mAP50-95，并保留 Params/GFLOPs。

## 7. 与本项目划分接近的可引用结果

### 7.1 精确同划分检索结论

本项目数据来自 2025 年发布的 Kaggle 转换包 *DIOR-R Dataset (YOLOv11-OBB Format)*，固定划分为 18770/2346/2347。截至 2026-07-20，未检索到同行评审论文明确使用这组精确数量；该数据页也没有公开 notebook、benchmark 结果或配套 checkpoint。因此暂时没有可以不经重训、又能声称“完全相同测试集”的外部方法。

### 7.2 推荐采用的近协议论文

Liu et al. 的 MS-YOLOv11（Sensors 2025，DOI `10.3390/s25196008`）与本项目最接近：使用 Ultralytics YOLO-OBB、20 类 DIOR-R、640 输入，模型约 2.87M 参数。论文采用 23190 张图像的 60/20/20 划分、batch 16、300 epochs，因而只能作为作者协议报告值。

| 方法 | Params | mAP50 (%) | mAP50-95 (%) | 数据来源 |
|---|---:|---:|---:|---|
| YOLOv8-OBB | 未报告 | 84.96 | 未报告 | MS-YOLOv11 论文复测 |
| YOLO11-OBB | 2,802,647 | 85.75 | 66.66 | MS-YOLOv11 论文复测 |
| MS-YOLOv11 | 2,865,383 | 88.33 | 70.90 | 原论文结果 |
| 本项目 YOLO11n-OBB | 2,657,623 | 85.88 | 68.74 | 本项目 80/10/10 test |
| 本项目 A-P2 + B-PKI-Lite | 2,740,390 | 88.59 | 71.98 | 本项目 80/10/10 test |

两套协议下的 YOLO11 baseline mAP50 仅相差 0.13 个百分点，说明结果量级接近；但这只是支持将其作为近协议参考的旁证，不证明测试集等价。正文可设一张带 `Reported under authors' settings` 脚注的补充表，不应据此宣称严格超过 MS-YOLOv11。

该文报告的 `mAP(small)=84.21` 不进入对比：虽然其文字定义也是面积小于 32x32，但数值与本项目小目标结果差异异常大，且没有公开评估实现可核验。小目标指标仅比较本项目统一脚本得到的 baseline/A/B/AB。

来源：[论文全文](https://www.mdpi.com/1424-8220/25/19/6008)；[本项目所用 Kaggle 数据页](https://www.kaggle.com/datasets/redzapdos123/dior-r-dataset-yolov11-obb-format)。

### 7.3 最省训练时间的最终方案

1. 本项目仅补跑 YOLOv8n-OBB 与 YOLO26n-OBB，得到完全同划分结果。
2. 主表放 baseline、YOLOv8n-OBB、YOLO26n-OBB、A、B、AB，全部是本项目同协议结果。
3. 另设一张很短的作者报告值表，放 MS-YOLOv11 论文中的 YOLOv8-OBB、YOLO11-OBB 和 MS-YOLOv11，并与本项目 AB 并列但明确分组和脚注。
4. 不再重训参数量较大的 Oriented R-CNN、ReDiffDet、PKINet-S 等模型。
