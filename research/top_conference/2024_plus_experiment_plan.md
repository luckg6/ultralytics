# 2024+ 新候选方向与后续实验计划

当前 DIOR-R 结果说明：

- A-P2 是最强单点改进，小目标 mAP50-95 提升明显。
- B-LSK 当前为负向消融，需要换思路。
- C-Dynamic 轻微正向，但单点说服力不足，适合与 A 融合或升级成更强方向感知模块。
- B-PKI-Lite 已完成第一版评估，比旧 B-LSK 明显更好，小目标 mAP50-95 相对 baseline 提升 +0.0151；已续训到 100 epoch，但 last100 低于 best。
- A+B-PKI-Lite 已完成 DIOR-R test 评估，是当前最佳结果：全尺度 mAP50-95 为 0.7198，小目标 mAP50-95 为 0.4288，相对 baseline 分别提升 +0.0324 和 +0.0818。
- C-Dynamic-Plus 已完成代码和配置，作为稍重一点的 C 单点复验版本，参数量 2,734,555，相对 baseline 增加 +2.90%。

## 已完成：A+B-PKI-Lite 融合

- 实验名：`dior_AB_p2_pki_lite`
- 配置：`experiments/dior/ab_p2_pki_lite.yaml`
- 服务器配置：`experiments/dior/ab_p2_pki_lite_homews.yaml`，使用 `/home/ws` 数据路径和 `batch=-1`
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-ab-p2-pki-lite.yaml`
- 动机：A-P2 提供高分辨率小目标检测分支，B-PKI-Lite 提供 neck 多核上下文融合，两者改动位置清楚分离，适合作为第一组融合实验。
- 当前状态：已完成训练和评估，是当前 DIOR-R test 最佳结果。相对 A-P2，全尺度 mAP50-95 继续提升 +0.0208，小目标 mAP50-95 继续提升 +0.0073。

## 优先级 2：A+C 融合

- 实验名建议：`dior_AC_p2_dynamic`
- 配置建议：`experiments/dior/ac_p2_dynamic.yaml`
- 模型建议：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-ac-p2-dynamic.yaml`
- 动机：A-P2 提供高分辨率小目标检测分支，C-Dynamic 提供轻量方向几何调制，两者可能互补。
- 风险：A-P2 已经增加 GFLOPs，融合 C 后要继续保持 `batch=4`。

## 优先级 2.5：C-Dynamic-Plus 单点复验

- 实验名：`dior_C_dynamic_plus`
- 配置：`experiments/dior/c_dynamic_plus.yaml`
- 服务器配置：`experiments/dior/c_dynamic_plus_homews.yaml`，使用 `/home/ws` 数据路径和 `batch=-1`
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-dynamic-plus.yaml`
- 模块：`C3k2GeoPlus`
- 动机：原 C-Dynamic 参数只增加 +0.73%，单点提升较弱；C-Dynamic-Plus 在同一 OBB head 位置使用更强方向几何调制，争取让 C 单点更有说服力。
- 当前状态：代码、配置、本地/服务器 dry-run、模型构建、预训练迁移和 dummy forward 均已通过。

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

## 优先级 4：GRA-Lite 升级 C

- 实验名建议：`dior_C_gra_lite`
- 配置建议：`experiments/dior/c_gra_lite.yaml`
- 模型建议：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-gra-lite.yaml`
- 模块建议：`C3k2GRA`
- 参考目录：`research/top_conference/gra_2024/`
- 动机：GRA 是 ECCV 2024 oriented object detection 工作，方向动机比当前 C-Dynamic 更强。
- 第一版落点：用 group-wise 方向 depthwise 分支近似 group-wise rotating，不引入自定义 CUDA。
- 风险：官方 GRA 依赖复杂，不能直接整体迁移。

## 优先级 5：GauCho 作为 OBB 回归扩展

- 实验名建议：`dior_C_gaussian_aux`
- 配置建议：`experiments/dior/c_gaussian_aux.yaml`
- 参考目录：`research/top_conference/gaucho_2025/`
- 动机：GauCho 针对 OBB 角度边界不连续问题，补足当前只改特征、不改 OBB 表示的不足。
- 第一版落点：不要替换 Ultralytics OBB head，先尝试训练期 Gaussian 辅助 loss。
- 风险：改 loss/head 影响面大，不建议作为下一次训练的首选。

## 暂不优先

- `CANConv`：遥感属性强，但原任务是 pansharpening，迁移到检测需要更强论证。
- `FDConv`：CVPR 2025 新，但频域动态卷积可能重，先作为备选。
- `YOLOv10`：适合作效率和训练策略参考，不适合作 A/B/C 主创新点。

## 当前建议路线

```text
短期：围绕 A+B-PKI-Lite 补第二数据集和论文表格
补充：C-Dynamic-Plus -> A+C 或 A+B+C
备选：B-FreqFuse -> C-GRA-Lite
论文扩展：GauCho-style Gaussian auxiliary loss
```
