# 2024+ 新候选方向与后续实验计划

> 冻结说明：本文件是 2026 年 7 月第三章 C 系列与 2024+ 候选方向的时间点记录，文中的“当前”“下一步”和服务器参数只描述当时状态，不再作为执行指令。第三章现已定稿为 FSPC-OBB，即 FSPB(A) + LPCF(B)；第四章入口为 `experiments/chapter4/README.md`。最新论文结果以 `paper/ippr2026/main.pdf` 为准。

当前 DIOR-R 结果说明：

- A-P2 是最强单点改进，小目标 mAP50-95 提升明显。
- B-LSK 当前为负向消融，需要换思路。
- C-Dynamic 轻微正向，但单点说服力不足，适合与 A 融合或升级成更强方向感知模块。
- B-PKI-Lite 已完成第一版评估，比旧 B-LSK 明显更好，小目标 mAP50-95 相对 baseline 提升 +0.0151；已续训到 100 epoch，但 last100 低于 best。
- A+B-PKI-Lite 已完成 DIOR-R test 评估，是当前最佳结果：全尺度 mAP50-95 为 0.7198，小目标 mAP50-95 为 0.4288，相对 baseline 分别提升 +0.0324 和 +0.0818。
- C-Dynamic-Plus 已完成训练和评估，作为稍重一点的 C 单点复验版本，比原 C-Dynamic 略好；全尺度 mAP50-95 为 0.6896，小目标 mAP50-95 为 0.3541，但单点提升仍不明显。
- A+B-PKI-Lite+C-Plus 已完成训练和评估，明显高于 baseline，但低于 A+B-PKI-Lite，说明当前三创新点简单叠加没有超过最佳双创新点组合。
- C-GRA-Lite 已完成训练和评估，参考 ECCV 2024 GRA 的 group-wise rotating / attention 思想，用标准 PyTorch 的方向掩码 depthwise 分支做轻量适配；小目标略高于 baseline，但全尺度 mAP50-95 和小目标 mAP50-95 均弱于 C-Dynamic-Plus。
- C-Chol-Lite 已完成训练和评估，明确避开 YOLO11 已有的 ProbIoU/Gaussian covariance/周期角度 loss，新增训练时 Cholesky/SPD 协方差辅助 head；全尺度 mAP50-95 为 0.6902，小目标 mAP50-95 为 0.3589，是该轮筛选最佳 C 单点。
- A+B-PKI-Lite+C-Chol-Lite 已完成训练和评估，全尺度 mAP50 为 0.8862，略高于 A+B-PKI-Lite，但全尺度 mAP50-95 为 0.7190、小目标 mAP50-95 为 0.4209，仍低于 A+B-PKI-Lite。
- A+B-PKI-Lite+C-SET-HBS 当时已完成代码和配置，参考 CVPR 2025 SET 的 HBS；该路线现已停止，不进入定稿方法。

## 已完成：A+B-PKI-Lite 融合

- 实验名：`dior_AB_p2_pki_lite`
- 配置：`experiments/dior/ab_p2_pki_lite.yaml`
- 服务器配置：`experiments/dior/ab_p2_pki_lite_homews.yaml`，使用 `/home/ws` 数据路径和 `batch=-1`
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-ab-p2-pki-lite.yaml`
- 动机：A-P2 提供高分辨率小目标检测分支，B-PKI-Lite 提供 neck 多核上下文融合，两者改动位置清楚分离，适合作为第一组融合实验。
- 当前状态：已完成训练和评估，是当前 DIOR-R test 最佳结果。相对 A-P2，全尺度 mAP50-95 继续提升 +0.0208，小目标 mAP50-95 继续提升 +0.0073。

## 已完成：A+B-PKI-Lite+C-Plus 三创新点融合

- 实验名：`dior_ABC_p2_pki_geo_plus`
- 配置：`experiments/dior/abc_p2_pki_geo_plus.yaml`
- 服务器配置：`experiments/dior/abc_p2_pki_geo_plus_homews.yaml`，使用 `/home/ws` 数据路径、`batch=-1` 和 `cache=ram`
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-abc-p2-pki-geo-plus.yaml`
- 权重：`weights/experiments/dior/abc_p2_pki_geo_plus/best.pt`
- 动机：验证 A 的 P2 小目标检测分支、B-PKI-Lite 的 neck 多核上下文融合和 C-Dynamic-Plus 的 head 方向几何适应能否继续正向叠加。
- 当前状态：已完成训练和 test 评估。全尺度 mAP50-95 为 0.7149，小目标 mAP50-95 为 0.4242；相对 baseline 分别提升 +0.0275 和 +0.0772，但相对 A+B-PKI-Lite 分别下降 -0.0049 和 -0.0046。因此 ABC 可作为三创新点消融行保留，主结果仍建议使用 A+B-PKI-Lite。

## 优先级 2：A+C 融合

- 实验名建议：`dior_AC_p2_dynamic`
- 配置建议：`experiments/dior/ac_p2_dynamic.yaml`
- 模型建议：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-ac-p2-dynamic.yaml`
- 动机：A-P2 提供高分辨率小目标检测分支，C-Dynamic 提供轻量方向几何调制，两者可能互补。
- 风险：A-P2 已经增加 GFLOPs，融合 C 后要继续保持 `batch=4`。

## 已完成：C-Dynamic-Plus 单点复验

- 实验名：`dior_C_dynamic_plus`
- 配置：`experiments/dior/c_dynamic_plus.yaml`
- 服务器配置：`experiments/dior/c_dynamic_plus_homews.yaml`，使用 `/home/ws` 数据路径和 `batch=-1`
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-dynamic-plus.yaml`
- 模块：`C3k2GeoPlus`
- 动机：原 C-Dynamic 参数只增加 +0.73%，单点提升较弱；C-Dynamic-Plus 在同一 OBB head 位置使用更强方向几何调制，争取让 C 单点更有说服力。
- 当前状态：已完成训练和 test 评估。相对 baseline，全尺度 mAP50-95 提升 +0.0022，小目标 mAP50-95 提升 +0.0071；相对 C-Dynamic，小目标 mAP50 提升 +0.0095，但小目标 mAP50-95 只提升 +0.0014。

## 已完成：重新设计 B，首选 PKINet 轻量版

- 实验名建议：`dior_B_pki_lite`
- 配置建议：`experiments/dior/b_pki_lite.yaml`
- 服务器配置：`experiments/dior/b_pki_lite_homews.yaml`，使用 `/home/ws` 数据路径和 `batch=-1`
- 模型建议：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-b-pki-lite.yaml`
- 模块建议：`C3k2PKI`
- 参考目录：`research/top_conference/pkinet_2024/`
- 动机：PKINet 是 CVPR 2024 遥感检测工作，直接针对遥感图像尺度变化和上下文多样性，比旧 B-LSK 更贴近本课题。
- 第一版落点：只替换 top-down neck 的 P5->P4、P4->P3 融合块，不加 P2 分支，不改 OBB 几何回归。
- 风险：不要整体搬 PKINet backbone；多大核分支必须用 depthwise 控制计算量。
- 当前状态：已完成第一版训练和 test 评估，并已续训到 100 epoch。`last_epoch100.pt` 低于 `best.pt`，最终对比建议使用 `best.pt`。

## 优先级 3：FreqFusion 轻量 neck 融合

- 实验名建议：`dior_B_freq_fuse`
- 配置建议：`experiments/dior/b_freq_fuse.yaml`
- 模型建议：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-b-freq-fuse.yaml`
- 模块建议：`FreqFuseLite`
- 参考目录：`research/top_conference/freqfusion_2024/`
- 动机：A-P2 已证明高分辨率特征重要，FreqFusion 的频率感知融合适合改善小目标细节和边界。
- 第一版落点：替换一次 P4->P3 或 P3->P2 的上采样融合，不做全 neck 替换。
- 风险：本次源码 clone 超时，需要手动或后续重试下载官方实现。

## 已完成：GRA-Lite 升级 C

- 实验名：`dior_C_gra_lite`
- 配置：`experiments/dior/c_gra_lite.yaml`
- 服务器配置：`experiments/dior/c_gra_lite_homews.yaml`，使用 `/home/ws` 数据路径、`batch=-1` 和 `cache=ram`
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-gra-lite.yaml`
- 模块：`C3k2GRA`
- 参考目录：`research/top_conference/gra_2024/`
- 动机：GRA 是 ECCV 2024 oriented object detection 工作，方向动机比当前 C-Dynamic 更强。
- 第一版落点：用水平、垂直、主对角和反对角四个方向掩码 depthwise 分支近似 group-wise rotating，再用输入自适应 routing 和 group/spatial attention 做融合；不引入自定义 CUDA。
- 检查状态：本地和 `/home/ws` dry-run 通过，模型构建和 dummy forward 正常；从 `weights/pretrained/yolo11n-obb.pt` 可迁移 490/679 项权重；构建检查参数量为 2,751,259。
- 当前状态：已完成训练和 test 评估。全尺度 mAP50-95 为 0.6861，小目标 mAP50-95 为 0.3522；相对 baseline 小目标 mAP50-95 提升 +0.0052，但相对 C-Dynamic-Plus 下降 -0.0019。
- 后续组合：`experiments/dior/abc_p2_pki_gra_lite.yaml` 和 `experiments/dior/abc_p2_pki_gra_lite_homews.yaml` 已 ready，构建检查参数量为 2,885,382，从预训练权重可迁移 297/905 项。
- 结论：不建议优先训练 ABC-GRA-Lite，继续改 C 时应换方向而不是加重 GRA。

## 已完成：C-Chol-Lite 作为 OBB 几何辅助 head

- 实验名：`dior_C_chol_lite`
- 配置：`experiments/dior/c_chol_lite.yaml`
- 服务器配置：`experiments/dior/c_chol_lite_homews.yaml`，使用 `/home/ws` 数据路径、`batch=-1` 和 `cache=ram`
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-chol-lite.yaml`
- 后续组合：`experiments/dior/abc_p2_pki_chol_lite.yaml` 和 `experiments/dior/abc_p2_pki_chol_lite_homews.yaml`
- 参考目录：`research/top_conference/gaucho_2025/`
- 动机：GauCho 启发 OBB 几何表征方向，但本仓库 YOLO11-OBB 已经有 ProbIoU、Gaussian covariance 相似度和周期角度 loss，所以不能再做普通 Gaussian loss。C-Chol-Lite 改为训练时额外预测 Cholesky/SPD 协方差参数，推理时仍使用原 YOLO11 OBB decode/NMS。
- 检查状态：本地和 `/home/ws` dry-run 通过；C-Chol-Lite 从预训练权重可迁移 490/583 项，构建检查参数量为 2,767,516；ABC-Chol-Lite 从预训练权重可迁移 297/777 项，构建检查参数量为 2,897,906；训练态 5 项 loss 和 eval 态无 `chol` 输出均正常。
- 当前状态：已完成训练和 test 评估。全尺度 mAP50-95 为 0.6902，小目标 mAP50-95 为 0.3589；相对 baseline 分别提升 +0.0028 和 +0.0119；相对 C-Dynamic-Plus 分别提升 +0.0006 和 +0.0048。
- ABC 组合结果：A+B-PKI-Lite+C-Chol-Lite 已完成训练和 test 评估。全尺度 mAP50-95 为 0.7190，小目标 mAP50-95 为 0.4209；相对 baseline 分别提升 +0.0316 和 +0.0739；相对 A+B-PKI-Lite 分别下降 -0.0008 和 -0.0079；相对 A+B-PKI-Lite+C-Plus 全尺度 mAP50-95 提升 +0.0041，但小目标 mAP50-95 下降 -0.0033。
- 结论：C-Chol-Lite 是该轮筛选最佳 C 单点，但叠加到 A+B 后没有超过 A+B-PKI-Lite；该结果只作历史探索记录。

## 暂不优先

- `CANConv`：遥感属性强，但原任务是 pansharpening，迁移到检测需要更强论证。
- `FDConv`：CVPR 2025 新，但频域动态卷积可能重，先作为备选。
- `YOLOv10`：适合作效率和训练策略参考，不适合作 A/B/C 主创新点。

## 待训练：A+B-PKI-Lite+C-SET-HBS

- 实验名：`dior_ABC_p2_pki_set_hbs`
- 本地配置：`experiments/dior/abc_p2_pki_set_hbs.yaml`，`batch=4`、`cache=disk`
- `/home/ws` 配置：`experiments/dior/abc_p2_pki_set_hbs_homews.yaml`，`batch=-1`、`cache=ram`
- 单独 C 配置：`experiments/dior/c_set_hbs.yaml` 和 `experiments/dior/c_set_hbs_homews.yaml`，供正式消融表使用
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-abc-p2-pki-set-hbs.yaml`
- 参考目录：`research/top_conference/set_2025/`
- 设计边界：A 仍是 P2 检测尺度，B 仍是 top-down neck 的 PKI 融合，C 只做训练时 head 辅助监督，不修改 neck、OBB decode、NMS 或评估协议。
- 轻量性：DIOR `nc=20` 构建参数求和 2,797,774，HBS 比 AB 增加 49,368；整体相对 baseline 构建参数约 +4.97%，推理路径和 AB 相同。
- 检查状态：本地和 `/home/ws` dry-run 通过；从官方预训练权重迁移 297/793 项；训练态 `set_loss`、反向梯度、eval 输出均正常。
- 预期：SET 在 DOTA-v2.0、AI-TOD、VisDrone 和 COCO 上同时改善总体与小目标指标，HBS 单项是论文消融中最主要的收益来源，因此比继续加重方向注意力更有机会与 AB 正向互补；最终是否超过 AB 必须以本次 DIOR-R test 为准。

## 当前建议路线

```text
短期：训练 A+B-PKI-Lite+C-SET-HBS，直接检验能否同时超过 AB 的全尺度和小目标指标
补充：A+B+C-Plus 和 A+B+C-Chol-Lite 均已完成但未超过 A+B-PKI-Lite；C-GRA-Lite 已完成但弱于 C-Plus；C-Chol-Lite 是当前最佳已完成 C 单点
备选：如果 SET-HBS 仍未超过 AB，再考虑完整 SET 的 API 或其他非重复 YOLO11 OBB 训练监督方向
论文扩展：Cholesky/SPD auxiliary head 或 GauCho-style 表征讨论，但不要重复 YOLO11 已有 ProbIoU/Gaussian covariance
```
