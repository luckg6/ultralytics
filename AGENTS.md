# 遥感旋转框小目标检测实验记录

这个仓库当前用于同时服务 EI 会议论文和毕业学位论文。研究对象不是泛化的目标检测，而是遥感影像小目标的 OBB 旋转框检测。基础模型选用 YOLO11n-OBB，主数据集先用 DIOR-R，后续再补第二个遥感 OBB 数据集。

仓库已按当前实验用途裁剪，官方 `docs/`、`examples/`、`docker/`、`.github/`、`tests/` 等通用工程文件不再保留；需要官方说明时查看在线 Ultralytics 文档。

## 基线设定

- 任务：遥感图像旋转框检测，`task=obb`。
- 当前统一训练入口：`scripts/train_obb.py`。
- DIOR-R 基线初始化方式：
  - 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-baseline.yaml`
  - 预训练权重：`weights/pretrained/yolo11n-obb.pt`
  - 数据集配置：`DIOR.yaml`
- DIOR-R 数据集配置文件：`ultralytics/cfg/datasets/DIOR.yaml`。
- DIOR-R 本地路径：`C:/E/datasets/YOLODIOR-R/`。
- 当前 DIOR-R 基线训练参数：
  - `epochs=100`
  - `batch=4`
  - `imgsz=640`
  - `seed=42`
  - `deterministic=True`
  - `amp=True`
  - `cache='disk'`
  - `cos_lr=True`
- 说明：早期 baseline 和 A-P2 尝试过更大的 batch，但 A-P2 在本机 RTX 4060 Laptop 8GB 上频繁 OOM 并触发 CPU fallback；显存占用仍偏高。后续正式主实验统一使用 `batch=4`，保证 baseline/A/B/C/AB/ABC 公平比较。
- 当前 DIOR-R 基线结果：`weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt`。
- 当前 DIOR-R baseline 原始训练日志：`runs/obb/train10/results.csv`。
- 当前 DIOR-R 基线在 `runs/obb/train10/results.csv` 中的验证指标：
  - mAP50 约为 0.849
  - mAP50-95 约为 0.670
- 当前 DIOR-R baseline 在 `test` split 上用 `scripts/evaluate_obb.py --mode both` 重评后的结果：
  - 全尺度 mAP50：0.8588
  - 全尺度 mAP50-95：0.6874
  - 小目标 mAP50：0.5146
  - 小目标 mAP50-95：0.3470
- 当前 DIOR-R baseline 参数量：2,657,623。

## 当前 A-P2 实验结果

- 创新点 A 已完成第一版实验，结构为 P2/4 OBB 检测分支。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-a-p2.yaml`。
- 实验配置：`experiments/dior/a_p2.yaml`。
- 训练后权重：`weights/experiments/dior/a_p2/best.pt`。
- 训练日志整理目录：`experiments/logs/dior/a_p2/`。
- 评估记录：
  - `weights/experiments/dior/a_p2/eval_dior_test_2026-07-06.md`
  - `weights/experiments/dior/a_p2/compare_with_baseline_dior_test_2026-07-06.md`
- 在 DIOR-R `test` split 上的评估结果：
  - 全尺度 mAP50：0.8779
  - 全尺度 mAP50-95：0.6990
  - 小目标 mAP50：0.5830
  - 小目标 mAP50-95：0.4215
- 相对 baseline 的提升：
  - 全尺度 mAP50：+0.0191
  - 全尺度 mAP50-95：+0.0116
  - 小目标 mAP50：+0.0684
  - 小目标 mAP50-95：+0.0745
- 参数量变化：
  - Params：2,698,340
  - 相对 baseline：+40,717（+1.53%）
- 结论：A-P2 对小目标提升明显，是有效创新点，后续 B、C 和融合实验可以继续以 A 为优先融合对象。

## 当前 B-LSK 实验结果

- 创新点 B 已完成第一版实验，结构为轻量 `SPPFLSK` 遥感上下文注意力。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-b-lsk.yaml`。
- 实验配置：`experiments/dior/b_lsk.yaml`。
- 训练后权重：`weights/experiments/dior/b_lsk/best.pt`。
- 训练日志整理目录：`experiments/logs/dior/b_lsk/`。
- 评估记录：
  - `weights/experiments/dior/b_lsk/eval_dior_test_2026-07-09.md`
  - `weights/experiments/dior/b_lsk/compare_with_baseline_a_p2_dior_test_2026-07-09.md`
- 在 DIOR-R `test` split 上的评估结果：
  - 全尺度 mAP50：0.8580
  - 全尺度 mAP50-95：0.6809
  - 小目标 mAP50：0.5070
  - 小目标 mAP50-95：0.3438
- 相对 baseline 的变化：
  - 全尺度 mAP50：-0.0008
  - 全尺度 mAP50-95：-0.0065
  - 小目标 mAP50：-0.0076
  - 小目标 mAP50-95：-0.0032
- 结论：当前 B-LSK 单独实验未提升，属于负向或无效消融；后续 B 以 B-PKI-Lite 为准，不再优先使用旧 B-LSK 做融合。

## 当前 B-PKI-Lite 实验结果

- 创新点 B 第二版已完成第一版训练和评估。
- 动机：旧 B-LSK 在 SPPF 位置追加上下文注意力后未提升，因此新版 B 改为 neck 特征融合层面的 PKINet 风格多核上下文增强。
- 参考论文：PKINet / Poly Kernel Inception Network for Remote Sensing Detection，CVPR 2024。
- 模块：`C3k2PKI`，在 `C3k2` 输出端追加轻量 `PKIContext`，使用 3x3、5x5、7x7 空洞 depthwise 多核分支和 CAA 风格上下文门控。
- 模块文件：`ultralytics/nn/modules/remote_obb_blocks.py`。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-b-pki-lite.yaml`。
- 本地实验配置：`experiments/dior/b_pki_lite.yaml`，`batch=4`。
- `/home/ws` 服务器实验配置：`experiments/dior/b_pki_lite_homews.yaml`，`batch=-1`，数据集配置为 `ultralytics/cfg/datasets/DIOR-homews.yaml`。
- 训练后权重：`weights/experiments/dior/b_pki_lite/best.pt`。
- 训练日志整理目录：`experiments/logs/dior/b_pki_lite/`。
- 评估记录：
  - `weights/experiments/dior/b_pki_lite/eval_dior_test_2026-07-11.md`
  - `weights/experiments/dior/b_pki_lite/compare_with_baseline_a_b_lsk_c_dior_test_2026-07-11.md`
- 设计位置：只替换 top-down neck 的 P5->P4、P4->P3 两个融合块，保持 OBB(P3, P4, P5) 检测头和层号不变。
- 与 A/C 的边界：
  - A 是宏观检测尺度改造，新增 P2/4 小目标检测分支。
  - B-PKI-Lite 是 neck 特征融合改造，不新增检测尺度。
  - C 是 OBB head 几何适应改造，不做 neck 多核融合。
- 训练和检查状态：
  - `python scripts/train_obb.py --config experiments/dior/b_pki_lite.yaml --env local --dry-run`
  - `python scripts/train_obb.py --config experiments/dior/b_pki_lite_homews.yaml --dry-run`
  - 模型构建成功。
  - dummy forward 正常。
  - 初始训练日志记录到 epoch 83/100，后续在本机续训到 epoch 100。
  - 由于续训时沿用了服务器 `save_dir=/home/ws/...`，本机续训输出被写到 `C:/home/ws/ultralytics/runs/obb/dior_B_pki_lite/`。
  - 训练期 val 最佳 mAP50-95 出现在 epoch 81，值为 0.67137。
  - test 评估参数量约 2,699,673，GFLOPs 约 6.8。
- 在 DIOR-R `test` split 上的评估结果：
  - 全尺度 mAP50：0.8588
  - 全尺度 mAP50-95：0.6885
  - 小目标 mAP50：0.5249
  - 小目标 mAP50-95：0.3621
- 相对 baseline 的变化：
  - 全尺度 mAP50：+0.0000
  - 全尺度 mAP50-95：+0.0011
  - 小目标 mAP50：+0.0103
  - 小目标 mAP50-95：+0.0151
- 参数量变化：
  - Params：2,699,673
  - 相对 baseline：+42,050（+1.58%）
- 100 epoch `last_epoch100.pt` 补充评估：
  - 全尺度 mAP50：0.8560
  - 全尺度 mAP50-95：0.6846
  - 小目标 mAP50：0.5225
  - 小目标 mAP50-95：0.3601
- 结论：B-PKI-Lite 比旧 B-LSK 明显更好，小目标提升也超过 C-Dynamic，但单点效果仍弱于 A-P2。续训到 100 epoch 后的 `last_epoch100.pt` 低于 `best.pt`，最终对比建议使用 `best.pt`。

## 当前 C-Dynamic 实验结果

- 创新点 C 已完成第一版实验，结构为轻量方向几何感知 `C3k2Geo` head 模块。
- 模块：`C3k2Geo`，在原 `C3k2` 输出端追加轻量方向几何感知注意力。
- 模块文件：`ultralytics/nn/modules/remote_obb_blocks.py`。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-dynamic.yaml`。
- 实验配置：`experiments/dior/c_dynamic.yaml`。
- 训练后权重：`weights/experiments/dior/c_dynamic/best.pt`。
- 训练日志整理目录：`experiments/logs/dior/c_dynamic/`。
- 评估记录：
  - `weights/experiments/dior/c_dynamic/eval_dior_test_2026-07-10.md`
  - `weights/experiments/dior/c_dynamic/compare_with_baseline_a_p2_b_lsk_dior_test_2026-07-10.md`
- 设计位置：只替换 OBB head 的 P3/P4/P5 三个输出融合层，保持 OBB(P3, P4, P5) 检测头和层号不变。
- 依赖：不需要下载 DCNv3/InternImage/Dynamic Head 官方代码，不需要自定义 CUDA/C++ op。
- 在 DIOR-R `test` split 上的评估结果：
  - 全尺度 mAP50：0.8562
  - 全尺度 mAP50-95：0.6884
  - 小目标 mAP50：0.5173
  - 小目标 mAP50-95：0.3527
- 相对 baseline 的变化：
  - 全尺度 mAP50：-0.0026
  - 全尺度 mAP50-95：+0.0010
  - 小目标 mAP50：+0.0027
  - 小目标 mAP50-95：+0.0057
- 参数量变化：
  - Params：2,676,940
  - 相对 baseline：+19,317（+0.73%）
- 结论：C-Dynamic 相对 baseline 有轻微正向收益，主要体现在 mAP50-95 和小目标指标，但单点效果明显弱于 A-P2；A+B-PKI-Lite 已完成并取得当前最佳结果，ABC 后续也已验证低于 A+B-PKI-Lite。

## 当前 C-Dynamic-Plus 实验结果

- C-Dynamic-Plus 已完成训练和评估，结果比原 C-Dynamic 略好，但仍属于轻微正向。
- 动机：原 C-Dynamic 改动较轻，参数量只比 baseline 增加 +0.73%，单点收益也较弱；C-Dynamic-Plus 在不覆盖原 C 的前提下加重 head 几何适应模块，争取获得更明显正向收益。
- 模块：`C3k2GeoPlus`，在 `C3k2` 输出端追加更强的方向几何注意力，包含通道压缩/还原、水平/垂直/空洞/交叉四方向 depthwise 分支、空间门控和通道门控。
- 模块文件：`ultralytics/nn/modules/remote_obb_blocks.py`。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-dynamic-plus.yaml`。
- 本地实验配置：`experiments/dior/c_dynamic_plus.yaml`，`batch=4`。
- `/home/ws` 服务器实验配置：`experiments/dior/c_dynamic_plus_homews.yaml`，`batch=-1`，数据集配置为 `ultralytics/cfg/datasets/DIOR-homews.yaml`。
- 训练后权重：`weights/experiments/dior/c_dynamic_plus/best.pt`。
- 原始输出权重：`runs/obb/dior_C_dynamic_plus/weights/best.pt`。
- 训练日志整理目录：`experiments/logs/dior/c_dynamic_plus/`。
- 评估记录：
  - `weights/experiments/dior/c_dynamic_plus/eval_dior_test_2026-07-14.md`
  - `weights/experiments/dior/c_dynamic_plus/compare_with_baseline_c_dior_test_2026-07-14.md`
- 设计位置：仍然只替换 OBB head 的 P3/P4/P5 三个输出融合层，保持 OBB(P3, P4, P5) 检测头和层号不变。
- 与 A/B 的边界：
  - 不新增 P2 检测分支，不做 A 的检测尺度改造。
  - 不替换 top-down neck 融合块，不做 B-PKI-Lite 的多核 neck 融合。
- 已通过检查：
  - `python scripts/train_obb.py --config experiments/dior/c_dynamic_plus.yaml --env local --dry-run`
  - `python scripts/train_obb.py --config experiments/dior/c_dynamic_plus_homews.yaml --dry-run`
  - 模型构建成功。
  - 从 `weights/pretrained/yolo11n-obb.pt` 可迁移 490/640 项权重。
  - dummy forward 正常。
- 在 DIOR-R `test` split 上的评估结果：
  - 全尺度 mAP50：0.8588
  - 全尺度 mAP50-95：0.6896
  - 小目标 mAP50：0.5268
  - 小目标 mAP50-95：0.3541
- 相对 baseline 的变化：
  - 全尺度 mAP50：+0.0000
  - 全尺度 mAP50-95：+0.0022
  - 小目标 mAP50：+0.0122
  - 小目标 mAP50-95：+0.0071
- 相对 C-Dynamic 的变化：
  - 全尺度 mAP50：+0.0026
  - 全尺度 mAP50-95：+0.0012
  - 小目标 mAP50：+0.0095
  - 小目标 mAP50-95：+0.0014
- 参数量变化：
  - Ultralytics 评估摘要 Params：2,696,431，GFLOPs：6.7
  - 相对 baseline：+38,808（+1.46%），GFLOPs +0.1
  - checkpoint 参数求和：2,704,215
- 结论：C-Dynamic-Plus 比 C-Dynamic 更稳一些，但提升幅度仍不明显；A+B-PKI-Lite+C-Plus 已验证低于 A+B-PKI-Lite，当前主线仍应优先围绕 A+B-PKI-Lite 补第二数据集和论文表格。

## 当前 C-GRA-Lite 实验结果

- C-GRA-Lite 已完成训练和评估，小目标略高于 baseline，但整体弱于 C-Dynamic-Plus。
- 动机：C-Dynamic/C-Dynamic-Plus 都只带来轻微正向，叠加到 A+B 后没有超过 A+B-PKI-Lite；新版 C 改为参考 ECCV 2024 GRA 的 group-wise rotating / attention 思想，增强 OBB head 对方向结构的建模能力。
- 外部材料状态：`research/external_repos/GRA` 和 `research/top_conference/gra_2024/` 已存在，不需要用户额外下载论文或源码。
- 模块：`C3k2GRA`，在 `C3k2` 输出端追加轻量 GRA-style 方向路由模块。
- 模块文件：`ultralytics/nn/modules/remote_obb_blocks.py`。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-gra-lite.yaml`。
- 本地实验配置：`experiments/dior/c_gra_lite.yaml`，`batch=4`。
- `/home/ws` 服务器实验配置：`experiments/dior/c_gra_lite_homews.yaml`，`batch=-1`，`cache=ram`，数据集配置为 `ultralytics/cfg/datasets/DIOR-homews.yaml`。
- 设计位置：只替换 OBB head 的 P3/P4/P5 三个输出融合层，保持 OBB(P3, P4, P5) 检测头和层号不变。
- 与 A/B 的边界：
  - 不新增 P2 检测分支，不做 A 的检测尺度改造。
  - 不替换 top-down neck 融合块，不做 B-PKI-Lite 的多核 neck 融合。
  - 不改 OBB loss、解码或后处理，暂不做 GauCho 式高风险回归头替换。
- 实现摘要：使用水平、垂直、主对角、反对角四个方向掩码 depthwise 分支近似 group-wise rotating，再用输入自适应 routing、group gate 和 spatial gate 做融合；全程只依赖标准 PyTorch。
- 已通过检查：
  - `python scripts/train_obb.py --config experiments/dior/c_gra_lite.yaml --env local --dry-run`
  - `python scripts/train_obb.py --config experiments/dior/c_gra_lite_homews.yaml --dry-run`
  - 模型构建成功。
  - 从 `weights/pretrained/yolo11n-obb.pt` 可迁移 490/679 项权重。
  - 构建检查参数量：2,751,259。
  - dummy forward 正常。
- 在 DIOR-R `test` split 上的评估结果：
  - 全尺度 mAP50：0.8583
  - 全尺度 mAP50-95：0.6861
  - 小目标 mAP50：0.5219
  - 小目标 mAP50-95：0.3522
- 相对 baseline 的变化：
  - 全尺度 mAP50：-0.0005
  - 全尺度 mAP50-95：-0.0013
  - 小目标 mAP50：+0.0073
  - 小目标 mAP50-95：+0.0052
- 相对 C-Dynamic-Plus 的变化：
  - 全尺度 mAP50：-0.0005
  - 全尺度 mAP50-95：-0.0035
  - 小目标 mAP50：-0.0049
  - 小目标 mAP50-95：-0.0019
- 参数量变化：
  - Ultralytics 评估摘要 Params：2,713,135，GFLOPs：6.7
  - 相对 baseline：+55,512（+2.09%），GFLOPs +0.1
  - checkpoint 参数求和：2,720,919
- 后续组合：A+B-PKI-Lite+C-GRA-Lite 配置也已 ready：
  - 本地配置：`experiments/dior/abc_p2_pki_gra_lite.yaml`
  - `/home/ws` 配置：`experiments/dior/abc_p2_pki_gra_lite_homews.yaml`
  - 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-abc-p2-pki-gra-lite.yaml`
  - 构建检查参数量：2,885,382。
  - 从 `weights/pretrained/yolo11n-obb.pt` 可迁移 297/905 项权重。
  - dummy forward 正常。
- 结论：C-GRA-Lite 小目标指标对 baseline 有轻微正向，但没有超过 C-Dynamic-Plus；当前不建议优先训练 A+B-PKI-Lite+C-GRA-Lite。

## 当前 C-Chol-Lite 实验结果

- C-Chol-Lite 已完成训练和评估，是当前最好的 C 单点版本。
- 设计动机：用户要求新的 C 方向必须确认不是 YOLO11 已有内容；本仓库 YOLO11-OBB 已有 `probiou`、基于 Gaussian covariance 的 OBB 相似度、旋转 TaskAlignedAssigner、DFL 和周期角度 loss，因此不再做普通 Gaussian/ProbIoU 变体。C-Chol-Lite 改为 YOLO11 没有的训练时 Cholesky/SPD 协方差辅助 head。
- 模块：`OBBCholesky`，继承标准 `OBB` head，额外预测每个 anchor 的 3 个 Cholesky/SPD 协方差参数。
- Loss：`chol_loss`，只在 `preds` 中存在 `chol` 时启用，普通 `OBB` 模型仍保持原来的 box/cls/dfl/angle 四项 loss。
- 推理：eval/inference 时不输出 `chol`，OBB decode、NMS 和评估协议与标准 YOLO11-OBB 保持一致。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-chol-lite.yaml`。
- 本地实验配置：`experiments/dior/c_chol_lite.yaml`，`batch=4`。
- `/home/ws` 服务器实验配置：`experiments/dior/c_chol_lite_homews.yaml`，`batch=-1`，`cache=ram`，数据集配置为 `ultralytics/cfg/datasets/DIOR-homews.yaml`。
- 与 A/B 的边界：
  - 不新增 P2 检测分支，不做 A 的检测尺度改造。
  - 不替换 top-down neck 融合块，不做 B-PKI-Lite 的多核 neck 融合。
  - 不改变推理解码、NMS 或评估后处理。
- 已通过检查：
  - `python scripts/train_obb.py --config experiments/dior/c_chol_lite.yaml --env local --dry-run`
  - `python scripts/train_obb.py --config experiments/dior/c_chol_lite_homews.yaml --dry-run`
  - 模型构建成功。
  - 从 `weights/pretrained/yolo11n-obb.pt` 可迁移 490/583 项权重。
  - 构建检查参数量：2,767,516。
  - 训练态输出包含 `chol`，loss 为 box/cls/dfl/angle/chol 五项。
  - eval 态输出不包含 `chol`，普通 OBB 输出 shape 正常。
- 训练输出：`runs/obb/dior_C_chol_lite/`。
- 训练后权重：`weights/experiments/dior/c_chol_lite/best.pt`。
- 训练日志整理目录：`experiments/logs/dior/c_chol_lite/`。
- 评估记录：
  - `weights/experiments/dior/c_chol_lite/eval_dior_test_2026-07-15.md`
  - `weights/experiments/dior/c_chol_lite/compare_with_baseline_cplus_ab_dior_test_2026-07-15.md`
- 训练摘要：
  - 服务器训练使用 `batch=-1`，`cache=ram`。
  - 训练期最佳 val mAP50-95：0.67428，出现在 epoch 99。
  - epoch 100 val mAP50-95：0.67426。
- 在 DIOR-R `test` split 上的评估结果：
  - 全尺度 mAP50：0.8577
  - 全尺度 mAP50-95：0.6902
  - 小目标 mAP50：0.5282
  - 小目标 mAP50-95：0.3589
- 相对 baseline 的变化：
  - 全尺度 mAP50：-0.0011
  - 全尺度 mAP50-95：+0.0028
  - 小目标 mAP50：+0.0136
  - 小目标 mAP50-95：+0.0119
- 相对 C-Dynamic-Plus 的变化：
  - 全尺度 mAP50：-0.0011
  - 全尺度 mAP50-95：+0.0006
  - 小目标 mAP50：+0.0014
  - 小目标 mAP50-95：+0.0048
- 参数量变化：
  - Ultralytics 评估摘要 Params：2,729,296，GFLOPs：6.6
  - 相对 baseline：+71,673（+2.70%），GFLOPs +0.0
  - 构建检查参数量：2,767,516
- 后续组合：A+B-PKI-Lite+C-Chol-Lite 配置也已 ready：
  - 本地配置：`experiments/dior/abc_p2_pki_chol_lite.yaml`
  - `/home/ws` 配置：`experiments/dior/abc_p2_pki_chol_lite_homews.yaml`
  - 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-abc-p2-pki-chol-lite.yaml`
  - 构建检查参数量：2,897,906。
  - 从 `weights/pretrained/yolo11n-obb.pt` 可迁移 297/777 项权重。
  - dummy forward 和训练态 5 项 loss 正常。
- 结论：C-Chol-Lite 单点优于 C-Dynamic-Plus 和 C-GRA-Lite，尤其小目标 mAP50-95 相对 C-Plus 提升 +0.0048；A+B-PKI-Lite+C-Chol-Lite 已完成训练和评估，仍未超过 A+B-PKI-Lite 的 mAP50-95 和小目标指标。

## 当前 A+B-PKI-Lite 融合实验结果

- A+B-PKI-Lite 已完成训练和评估，是当前 DIOR-R test 上的最佳结果。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-ab-p2-pki-lite.yaml`。
- 本地实验配置：`experiments/dior/ab_p2_pki_lite.yaml`，`batch=4`。
- `/home/ws` 服务器实验配置：`experiments/dior/ab_p2_pki_lite_homews.yaml`，`batch=-1`，数据集配置为 `ultralytics/cfg/datasets/DIOR-homews.yaml`。
- 训练后权重：`weights/experiments/dior/ab_p2_pki_lite/best.pt`。
- 原始输出权重：`runs/obb/dior_AB_p2_pki_lite/weights/best.pt`。
- 训练日志整理目录：`experiments/logs/dior/ab_p2_pki_lite/`。
- 评估记录：
  - `weights/experiments/dior/ab_p2_pki_lite/eval_dior_test_2026-07-13.md`
  - `weights/experiments/dior/ab_p2_pki_lite/compare_with_baseline_a_b_pki_c_dior_test_2026-07-13.md`
- 设计边界：
  - 保留 A-P2 的 P2/4 检测分支，OBB 输出为 OBB(P2, P3, P4, P5)。
  - 只在原 top-down neck 的 P5->P4、P4->P3 融合块使用 `C3k2PKI`。
  - 新增的 P3->P2 分支保持普通 `C3k2`，避免把 B 的 neck 融合改造混到 A 的检测尺度创新里。
- 训练和检查状态：
  - `python scripts/train_obb.py --config experiments/dior/ab_p2_pki_lite.yaml --env local --dry-run`
  - `python scripts/train_obb.py --config experiments/dior/ab_p2_pki_lite_homews.yaml --dry-run`
  - 模型构建成功。
  - 从 `weights/pretrained/yolo11n-obb.pt` 可迁移 297/721 项权重。
  - dummy forward 正常。
- 在 DIOR-R `test` split 上的评估结果：
  - 全尺度 mAP50：0.8859
  - 全尺度 mAP50-95：0.7198
  - 小目标 mAP50：0.5958
  - 小目标 mAP50-95：0.4288
- 相对 baseline 的变化：
  - 全尺度 mAP50：+0.0271
  - 全尺度 mAP50-95：+0.0324
  - 小目标 mAP50：+0.0812
  - 小目标 mAP50-95：+0.0818
- 相对 A-P2 的变化：
  - 全尺度 mAP50：+0.0080
  - 全尺度 mAP50-95：+0.0208
  - 小目标 mAP50：+0.0128
  - 小目标 mAP50-95：+0.0073
- 参数量变化：
  - Ultralytics 评估摘要 Params：2,740,390，GFLOPs：10.7
  - 相对 baseline：+82,767（+3.11%），GFLOPs +4.1
  - checkpoint 参数求和：2,748,406
- 结论：A+B-PKI-Lite 相对 baseline 和 A-P2 都继续提升，说明 A 的 P2 小目标检测分支与 B-PKI-Lite 的 neck 多核上下文融合存在正向互补。当前建议把该模型作为 DIOR-R 主结果候选。

## 当前 A+B-PKI-Lite+C-Plus 融合实验结果

- A+B-PKI-Lite+C-Plus 已完成训练和评估，结果明显高于 baseline，但低于 A+B-PKI-Lite。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-abc-p2-pki-geo-plus.yaml`。
- 本地实验配置：`experiments/dior/abc_p2_pki_geo_plus.yaml`，`batch=4`。
- `/home/ws` 服务器实验配置：`experiments/dior/abc_p2_pki_geo_plus_homews.yaml`，`batch=-1`，`cache=ram`，数据集配置为 `ultralytics/cfg/datasets/DIOR-homews.yaml`。
- 训练后权重：`weights/experiments/dior/abc_p2_pki_geo_plus/best.pt`。
- 原始输出权重：`runs/obb/dior_ABC_p2_pki_geo_plus/weights/best.pt`。
- 训练日志整理目录：`experiments/logs/dior/abc_p2_pki_geo_plus/`。
- 评估记录：
  - `weights/experiments/dior/abc_p2_pki_geo_plus/eval_dior_test_2026-07-14.md`
  - `weights/experiments/dior/abc_p2_pki_geo_plus/compare_with_baseline_ab_cplus_dior_test_2026-07-14.md`
- 设计边界：
  - A：新增 P2/4 小目标检测分支，OBB 输出为 OBB(P2, P3, P4, P5)。
  - B-PKI-Lite：只在原 top-down neck 的 P5->P4、P4->P3 融合块使用 `C3k2PKI`。
  - C-Plus：在 OBB(P2/P3/P4/P5) 四个最终输出融合层使用 `C3k2GeoPlus` 做方向几何适应。
- 已通过检查：
  - `python scripts/train_obb.py --config experiments/dior/abc_p2_pki_geo_plus.yaml --env local --dry-run`
  - `python scripts/train_obb.py --config experiments/dior/abc_p2_pki_geo_plus_homews.yaml --dry-run`
  - 模型构建成功。
  - 从 `weights/pretrained/yolo11n-obb.pt` 可迁移 297/853 项权重。
  - 构建检查参数量：2,863,110。
  - dummy forward 正常。
- 在 DIOR-R `test` split 上的评估结果：
  - 全尺度 mAP50：0.8832
  - 全尺度 mAP50-95：0.7149
  - 小目标 mAP50：0.5838
  - 小目标 mAP50-95：0.4242
- 相对 baseline 的变化：
  - 全尺度 mAP50：+0.0244
  - 全尺度 mAP50-95：+0.0275
  - 小目标 mAP50：+0.0692
  - 小目标 mAP50-95：+0.0772
- 相对 A+B-PKI-Lite 的变化：
  - 全尺度 mAP50：-0.0027
  - 全尺度 mAP50-95：-0.0049
  - 小目标 mAP50：-0.0120
  - 小目标 mAP50-95：-0.0046
- 参数量变化：
  - Ultralytics 评估摘要 Params：2,784,390，GFLOPs：11.1
  - 相对 baseline：+126,767（+4.77%），GFLOPs +4.5
  - 相对 A+B-PKI-Lite：+44,000，GFLOPs +0.4
- 结论：ABC 证明三创新点叠加仍能显著优于 baseline，但没有超过 A+B-PKI-Lite；当前论文主结果候选仍建议使用 A+B-PKI-Lite，ABC 作为三创新点融合消融行保留。

## 当前 A+B-PKI-Lite+C-Chol-Lite 融合实验结果

- A+B-PKI-Lite+C-Chol-Lite 已完成训练和评估，结果明显高于 baseline，全尺度 mAP50 略高于 A+B-PKI-Lite，但 mAP50-95 和小目标指标低于 A+B-PKI-Lite。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-abc-p2-pki-chol-lite.yaml`。
- 本地实验配置：`experiments/dior/abc_p2_pki_chol_lite.yaml`，`batch=4`。
- `/home/ws` 服务器实验配置：`experiments/dior/abc_p2_pki_chol_lite_homews.yaml`，`batch=-1`，`cache=ram`，数据集配置为 `ultralytics/cfg/datasets/DIOR-homews.yaml`。
- AutoDL 双 RTX 3090 一次性续训配置：
  - 实验配置：`experiments/dior/abc_p2_pki_chol_lite_autodl3090.yaml`
  - 环境配置：`environments/autodl_3090_once.yaml`
  - 说明文档：`AUTODL_3090_ONCE.md`
- 训练后权重：`weights/experiments/dior/abc_p2_pki_chol_lite/best.pt`。
- 原始输出权重：`runs/obb/dior_ABC_p2_pki_chol_lite/weights/best.pt`。
- 训练日志整理目录：`experiments/logs/dior/abc_p2_pki_chol_lite/`。
- 评估记录：
  - `weights/experiments/dior/abc_p2_pki_chol_lite/eval_dior_test_2026-07-16.md`
  - `weights/experiments/dior/abc_p2_pki_chol_lite/compare_with_baseline_ab_cplus_dior_test_2026-07-16.md`
- 设计边界：
  - A：新增 P2/4 小目标检测分支，OBB 输出为 OBB(P2, P3, P4, P5)。
  - B-PKI-Lite：只在原 top-down neck 的 P5->P4、P4->P3 融合块使用 `C3k2PKI`。
  - C-Chol-Lite：在 OBB head 上新增训练时 Cholesky/SPD 协方差辅助分支，推理和评估时仍使用标准 OBB 输出。
- 训练摘要：
  - 先在 `/home/ws` 服务器训练到 epoch 16 左右，后续拷到本机和 AutoDL 继续续训。
  - AutoDL 双 RTX 3090 续训时，配置改为 `device="0,1"`、`cache=ram`，多卡 DDP 不支持 `batch=-1`，最终用 `--batch 32` 跑完。
  - 训练期最佳 val mAP50-95：0.70558，出现在 epoch 100。
  - epoch 100 val mAP50：0.88188。
- 在 DIOR-R `test` split 上的评估结果：
  - 全尺度 mAP50：0.8862
  - 全尺度 mAP50-95：0.7190
  - 小目标 mAP50：0.5774
  - 小目标 mAP50-95：0.4209
- 相对 baseline 的变化：
  - 全尺度 mAP50：+0.0274
  - 全尺度 mAP50-95：+0.0316
  - 小目标 mAP50：+0.0628
  - 小目标 mAP50-95：+0.0739
- 相对 A+B-PKI-Lite 的变化：
  - 全尺度 mAP50：+0.0003
  - 全尺度 mAP50-95：-0.0008
  - 小目标 mAP50：-0.0184
  - 小目标 mAP50-95：-0.0079
- 相对 A+B-PKI-Lite+C-Plus 的变化：
  - 全尺度 mAP50：+0.0030
  - 全尺度 mAP50-95：+0.0041
  - 小目标 mAP50：-0.0064
  - 小目标 mAP50-95：-0.0033
- 参数量变化：
  - Ultralytics 评估摘要 Params：2,819,058，GFLOPs：10.7
  - 相对 baseline：+161,435（+6.07%），GFLOPs +4.1
  - 相对 A+B-PKI-Lite：+78,668（+2.87%），GFLOPs +0.0
  - 构建检查参数量：2,897,906
- 结论：ABC-Chol 比 ABC-Plus 的全尺度 mAP50/mAP50-95 更高，但小目标指标更低；与 A+B-PKI-Lite 相比，只有全尺度 mAP50 略高，mAP50-95 和小目标指标仍低。因此当前论文主结果候选仍建议使用 A+B-PKI-Lite，ABC-Chol 可作为三创新点融合消融行或补充结果。

## 待训练 A+B-PKI-Lite+C-SET-HBS 融合实验

- 目标：争取让 ABC 在全尺度和小目标指标上同时超过当前 A+B-PKI-Lite。
- 参考论文：SET / Spectral Enhancement for Tiny Object Detection，CVPR 2025。
- 采用范围：只采用论文中消融收益最大的 HBS，不声称复现包含 API 的完整 SET。
- 模块：`OBBSETHBS`，继承标准 `OBB` head，并注册四个训练期背景平滑适配器。
- 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-abc-p2-pki-set-hbs.yaml`。
- 本地配置：`experiments/dior/abc_p2_pki_set_hbs.yaml`，`batch=4`、`cache=disk`。
- `/home/ws` 配置：`experiments/dior/abc_p2_pki_set_hbs_homews.yaml`，`batch=-1`、`cache=ram`。
- 单独 C 配置：`experiments/dior/c_set_hbs.yaml` 和 `experiments/dior/c_set_hbs_homews.yaml`，用于最终消融表；可在 ABC 验证成功后补训。
- 参考材料：`research/top_conference/set_2025/README.md` 和 `SET_CVPR2025.pdf`；截至 2026-07-16 未检索到论文官方源码，不需要用户额外下载材料。
- 设计边界：
  - A 仍只负责新增 P2/4 小目标检测分支。
  - B-PKI-Lite 仍只负责原 top-down neck 的 P5->P4、P4->P3 融合。
  - C 只在训练时根据旋转 GT 生成前景掩码，保留前景并平滑背景，再通过共享 OBB head 形成辅助检测监督。
  - 验证和推理不执行 HBS，不改变 OBB decode、NMS 或评估协议。
- 超参数：通道压缩率 `r=4`，辅助检测损失权重 `set_hbs=1.0`，均采用论文推荐值。
- 参数量：
  - DIOR `nc=20` 构建参数求和：2,797,774。
  - HBS 相对同口径 AB 增加 49,368。
  - 相对同口径 baseline 增加约 132,367（约 +4.97%）。
  - 按现有 Ultralytics 评估摘要差值口径预计 Params 约 2,789,758，最终以训练后 `best.pt` 评估输出为准。
- 已通过检查：
  - 本地与 `/home/ws` dry-run 正常。
  - 四层 stride 为 4/8/16/32。
  - 从 `weights/pretrained/yolo11n-obb.pt` 可迁移 297/793 项权重。
  - 训练态输出包含 `set_feats`，loss 为 box/cls/dfl/angle/set 五项，HBS 参数有有效反向梯度。
  - eval 输出不包含 `set_feats`，输出 shape 和普通 AB 一致。
  - 普通 A/B/C/baseline 模型仍使用原 4 项 OBB loss，不受该实验影响。
- 状态：代码与配置 ready，待训练；能否超过 AB 必须以 DIOR-R `test --mode both` 的最终结果为准。

## 跨数据集基线原则

第二个数据集的 baseline 不应该使用 DIOR-R 训练得到的 `best.pt` 继续训练。

正确做法：

```text
weights/pretrained/yolo11n-obb.pt -> 第二个数据集训练 -> 第二个数据集 baseline best.pt
```

不推荐做法：

```text
weights/pretrained/yolo11n-obb.pt -> DIOR-R 训练得到 best.pt -> 第二个数据集继续训练
```

原因：DIOR-R 训练后的 `best.pt` 已经带有 DIOR-R 的领域适配信息，如果再拿它作为第二个数据集的 baseline 初始化，会让 baseline 不再是纯粹的 YOLO11n-OBB baseline，后续消融对比也不公平。

两个数据集上的实验应保持同一逻辑：

```text
DIOR-R:
baseline/A/B/C/AB/ABC 都从 weights/pretrained/yolo11n-obb.pt 起训

第二数据集:
baseline/A/B/C/AB/ABC 也都从 weights/pretrained/yolo11n-obb.pt 起训
```

除非论文明确做“跨数据集迁移学习”实验，否则不要把 DIOR-R 的 `best.pt` 用到第二个数据集的主实验里。

## 数据集说明

- DIOR-R 是第一个数据集，也建议作为论文主数据集。
- UCAS-AOD 已确定为 EI 会议论文的第二个数据集，本地目录为 `C:/E/datasets/UCAS-AOD-YOLO/`，`/home/ws` 目录为 `/home/ws/datasets/UCAS-AOD-YOLO/`。
- UCAS-AOD 固定使用 755/302/453 的 train/val/test 划分，共 14597 个 OBB 实例；在 `imgsz=640` 下按本项目 `w*h<1024` 协议统计，小目标约占 71%。
- UCAS-AOD 只做 baseline、A-P2、B-PKI-Lite、A+B-PKI-Lite 四组 EI 论文消融，配置位于 `experiments/ucas_aod/`。
- UCAS-AOD 本地配置固定 `batch=4`、`cache=disk`；`/home/ws` 配置固定使用 1 号 GPU（`device=1`）、`batch=-1`、`cache=ram`。
- UCAS-AOD 四组实验已完成，test 结果为：baseline 0.8017/0.7393、A-P2 0.7946/0.7291、B-PKI-Lite 0.8026/0.7434、AB 0.7930/0.7306，数值顺序为全尺度/小目标 mAP50-95。
- UCAS-AOD 自动 batch 初轮中 B-PKI-Lite 四项指标均略高于 baseline；固定 `batch=32` 复核后，B 仅小目标 mAP50/mAP50-95 稳定提升，全尺度 mAP50-95 略低于 baseline。A-P2 和 AB 在两轮中都未复现 DIOR-R 增益。
- 本轮四组使用 `batch=-1`，每 epoch 批次数分别为 14/23/16/24，说明自动 batch 随结构变化；严格论文对比建议最终以共同固定 batch 复核。
- UCAS-AOD 已新增四份 `batch=32` 的 `/home/ws` 复核配置，文件名以 `_homews_batch32_verify.yaml` 结尾；它们使用 `device=1`、`cache=ram` 和独立的 `_b32_verify` 输出目录，不覆盖原始自动 batch 结果。
- 固定 batch 复核结果为：baseline 0.8024/0.7371、A-P2 0.7921/0.7321、B-PKI-Lite 0.8006/0.7410、AB 0.7930/0.7306，数值顺序为全尺度/小目标 mAP50-95。详细记录位于 `weights/experiments/ucas_aod/eval_ucas_aod_test_batch32_2026-07-17.md`。
- VEDAI-1024 已作为新的轻量微小目标 OBB 筛选数据集完成转换。本地原始目录为 `C:/E/datasets/VEDAI-1024/`，YOLO-OBB 输出为 `C:/E/datasets/VEDAI-1024-YOLO/`，服务器目录约定为 `/home/ws/datasets/VEDAI-1024-YOLO/`。
- VEDAI 转换脚本为 `scripts/convert_vedai_to_yolo_obb.py`，只使用彩色 `_co.png`，九类采用官方 DevKit 定义，原始类别 7/8 共 7 个非官方稀有实例被记录并忽略。
- VEDAI 固定筛选划分在训练前按类别直方图确定：官方 fold10 test、fold02 val、其余八个 fold train，对应 968/121/121 张图和 2950/368/369 个 OBB；约 96% 的目标在 `imgsz=640` 下满足 `w*h<1024`。
- VEDAI 本地与 `/home/ws` 的 baseline/A/B/AB 配置位于 `experiments/vedai/`。服务器筛选固定 `batch=32`、`device=1`、`cache=ram`，不使用自动 batch。
- VEDAI 四组实验已完成，fold10 test 的全尺度/小目标 mAP50-95 为：baseline 0.5661/0.5293、A-P2 0.4687/0.4311、B-PKI-Lite 0.5756/0.5365、AB 0.4994/0.4674。
- VEDAI 上只有 B-PKI-Lite 四项指标全部超过 baseline；A-P2 和 AB 都明显负向。AB 相对 A 有回升，但仍未超过 baseline。
- VEDAI 当前结果是固定 fold10 单划分筛选，不是十折交叉验证均值。详细记录位于 `weights/experiments/vedai/eval_vedai_fold10_test_2026-07-17.md`。
- 由于 VEDAI 不支持 A/AB 的跨数据集增益，不建议将其作为 AB 主方法的第二数据集主结果；可保留为 B 的辅助证据和负向数据集筛选记录。
- VEDAI 专用 A-P2-Plus 已完成训练和评估：模型为 `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-a-p2-plus.yaml`，本地配置为 `experiments/vedai/a_p2_plus.yaml`，`/home/ws` 固定 batch 配置为 `experiments/vedai/a_p2_plus_homews_batch32.yaml`。
- A-P2-Plus 保留 P2/4 检测分支，将 P2 实际通道从 32 增到 48、有效重复从 1 增到 2，并用独立 `C3k2P2Guard/P2SemanticGuard` 学习抑制缺少语义支持的 P2 背景响应；不使用 B 的 PKI 模块。
- A-P2-Plus 在 VEDAI `nc=9` 下构建参数量 2,803,925，13.8 GFLOPs；相对同口径 baseline 增加 140,663（约 `+5.28%`）。四层 stride 4/8/16/32、预训练迁移 297/694 项、dummy forward 和守门反向梯度均已通过。
- A-P2-Plus fold10 test 结果为：全尺度 0.7310/0.5507，小目标 0.7054/0.5444，数值顺序为 mAP50/mAP50-95。小目标相对 baseline 提升 `+0.0223/+0.0151`，也高于 B `+0.0040/+0.0079`；全尺度 mAP50-95 仍比 baseline 低 `0.0154`。
- A-P2-Plus 权重位于 `weights/experiments/vedai/a_p2_plus/best.pt`，日志位于 `experiments/logs/vedai/a_p2_plus/`。当前 B 全尺度最佳，A-P2-Plus 小目标最佳，已据此新建独立 AB-Plus，不覆盖旧 AB。
- VEDAI AB-Plus 已完成训练和评估：模型为 `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-ab-p2-plus-pki-lite.yaml`，本地配置为 `experiments/vedai/ab_p2_plus_pki_lite.yaml`，`/home/ws` 配置为 `experiments/vedai/ab_p2_plus_pki_lite_homews_batch32.yaml`。
- AB-Plus 中第 13/16 层为 B 的 `C3k2PKI`，第 19 层为 A-Plus 的 `C3k2P2Guard`，OBB 仍输出 stride 4/8/16/32；不改 loss、解码或 NMS，不覆盖旧 AB。
- AB-Plus 在 VEDAI `nc=9` 下构建参数量 2,845,975，14.0 GFLOPs，相对同口径 baseline 参数增加 182,713（约 `+6.86%`），相对 A-P2-Plus 只增加 42,050。
- AB-Plus fold10 test 结果为全尺度 0.6862/0.5263、小目标 0.6501/0.4955，数值顺序为 mAP50/mAP50-95；相对 baseline 四项下降 `-0.0438/-0.0398/-0.0330/-0.0338`。
- AB-Plus 比旧 AB 四项回升 `+0.0080/+0.0269/+0.0181/+0.0281`，但比 A-P2-Plus 和 B 都低；当前串联结构下 B 恢复了部分召回，但冲淡了 P2SemanticGuard 的误检抑制。
- AB-Plus 权重位于 `weights/experiments/vedai/ab_p2_plus_pki_lite/best.pt`，日志位于 `experiments/logs/vedai/ab_p2_plus_pki_lite/`。
- VEDAI AB-Plus-Decoupled 已完成训练和评估：模型为 `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-ab-p2-plus-pki-decoupled.yaml`，本地配置为 `experiments/vedai/ab_p2_plus_pki_decoupled.yaml`，`/home/ws` 配置为 `experiments/vedai/ab_p2_plus_pki_decoupled_homews_batch32.yaml`。
- 解耦版保留 A-P2-Plus 0-28 层主路，B 另建独立 PKI top-down 路径，通过零初始化 `ResidualFeatureBlend` 只在最终 P3/P4 注入，不改变 P2SemanticGuard 的输入。
- AB-Plus-Decoupled 在 VEDAI `nc=9` 下构建参数量 2,989,559，14.8 GFLOPs，相对 baseline 参数增加 326,297（约 `+12.25%`）。
- 解耦版 fold10 test 结果为全尺度 0.7336/0.5487、小目标 0.6768/0.5222，数值顺序为 mAP50/mAP50-95。相对串联 AB-Plus 四项回升 `+0.0474/+0.0224/+0.0267/+0.0267`，但除全尺度 mAP50 外仍未超过 baseline。
- 解耦版的 P3/P4 融合幅度均约 1.2%，但 P2Guard 抑制仍比单独 A-Plus 弱。若继续，下一步应从 A-P2-Plus `best.pt` 阶段初始化并保护主路，只学习 B 残差。
- 解耦版权重位于 `weights/experiments/vedai/ab_p2_plus_pki_decoupled/best.pt`，日志位于 `experiments/logs/vedai/ab_p2_plus_pki_decoupled/`。
- VEDAI AB-PKI-Heavy 已 ready：模型为 `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-ab-p2-plus-pki-heavy.yaml`，本地配置为 `experiments/vedai/ab_p2_plus_pki_heavy.yaml`，`/home/ws` 配置为 `experiments/vedai/ab_p2_plus_pki_heavy_homews_batch32.yaml`。
- Heavy 版是单路 neck：P2Guard 之前保持普通融合，P2 实际通道提高到 64；B 的 `C3k2PKI` 放在 P2 之后的最终 P3/P4 融合，实际通道为 96/160，P2/P3/P4 融合有效重复数均为 2。
- Heavy 版在 VEDAI `nc=9` 下构建参数量 3,580,431，20.2 GFLOPs，相对 baseline 参数增加 917,169（约 `+34.44%`），但绝对规模仍只有约 3.6M，论文中必须明确标记为 Heavy。
- Heavy 版已通过本地和 `/home/ws` dry-run、预训练迁移 297/790 项、dummy forward `(1, 14, 34000)`、四层 stride 4/8/16/32 与 P2Guard/PKI 反向梯度检查，当前待训练。
- 最终论文表格建议统一使用同一个 split，例如都用 `split='test'`，确保所有模型公平比较。
- `cache='disk'` 会在 images 文件夹下生成 `.npy` 缓存文件，统计原始图片数量时不要把 `.npy` 算进去。

## 小目标评估

仓库当前在 `ultralytics/models/yolo/obb/val.py` 里加入了自定义小目标评估开关，通过环境变量 `EVAL_SMALL_ONLY` 控制。注意这里的 `val.py` 是 Ultralytics 的 OBB 核心验证器文件，不是 `scripts/val.py` 这个项目脚本。

- `EVAL_SMALL_ONLY=0`：正常评估所有尺度目标。
- `EVAL_SMALL_ONLY=1`：只保留 `w * h < 1024` 的 GT 框和预测框。
- 在 `imgsz=640` 时，这大致对应模型输入尺度下小于 `32x32` 的目标。
- 论文中建议表述为“自定义小目标评估协议”，不要写成官方 Ultralytics 原生指标。

## 验证脚本现状

- 当前统一评估入口：`scripts/evaluate_obb.py`。
- 旧的 `scripts/val.py` 和 `scripts/val_new.py` 已删除，避免后续误用。
- `scripts/evaluate_obb.py` 支持传参，不再需要为每个模型手改硬编码路径。
- 默认会评估 `weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt` 在 `DIOR.yaml` 的 `test` split 上的全尺度和小目标结果。

常用命令：

```bash
python scripts/evaluate_obb.py
python scripts/evaluate_obb.py --model weights/baselines/dior-r/yolo11n-obb-dior-r-best.pt --data DIOR.yaml --split test --mode both
python scripts/evaluate_obb.py --model weights/experiments/dior/a_p2/best.pt --data DIOR.yaml --split test --mode both
python scripts/evaluate_obb.py --model weights/experiments/dior/abc_p2_pki_geo_plus/best.pt --data DIOR.yaml --split test --mode both
python scripts/evaluate_obb.py --model weights/experiments/dior/abc_p2_pki_chol_lite/best.pt --data DIOR.yaml --split test --mode both
python scripts/evaluate_obb.py --model path/to/best.pt --data DOTAv1.yaml --split test --mode all
python scripts/evaluate_obb.py --model path/to/best.pt --data DIOR.yaml --mode small
```

## 实验矩阵

每个数据集上建议做 1 个 baseline 加 5 个改进实验：

1. Baseline：YOLO11n-OBB。
2. 创新点 A：P2/4 小目标检测分支，当前 DIOR-R test 已验证有效。
3. 创新点 B：轻量 `SPPFLSK` 遥感上下文注意力，当前已评估但未提升。
4. 创新点 C：C-Dynamic、C-Dynamic-Plus、C-GRA-Lite 和 C-Chol-Lite 均已完成；C-Chol-Lite 是当前最佳已完成 C 单点。新的训练监督方向 C-SET-HBS 已完成 ABC 配置，待训练。
5. 双创新点融合：A+B-PKI-Lite 已完成并取得当前最佳结果；如需补充，可继续做 A+C。
6. 三创新点融合：A+B-PKI-Lite+C-Plus 和 A+B-PKI-Lite+C-Chol-Lite 均已完成但未超过 A+B-PKI-Lite；下一组优先训练 A+B-PKI-Lite+C-SET-HBS。

如果按“改进实验”计数，两个数据集是 `5 x 2 = 10` 个实验。
如果按论文表格行数计数，两个数据集都要包含 baseline，因此是 `6 x 2 = 12` 行。

建议论文表格：

- 主结果表：P、R、mAP50、mAP50-95、Params、GFLOPs、FPS 或 inference time。
- 消融实验表：baseline、A、B、C、最佳双融合、A+B+C。
- 小目标表：baseline 和最终模型的全尺度 mAP、小目标 mAP。
- 分类别表：可选，DIOR-R 上可以重点看 vehicle、ship、bridge、harbor、storagetank 等类别。

## 结构变体管理规范

后续做 A、B、C、AB、ABC 时，网络结构一定会变化，而且单个创新点不一定有效。为了保持实验有序，不允许靠反复手改同一个原始网络文件来做对比实验。

核心原则：

- 原始 YOLO11n-OBB 结构尽量不动，`ultralytics/cfg/models/11/yolo11-obb.yaml` 和官方基础模块保持可追溯。
- 每个结构变体使用独立 model YAML，结构差异写在 YAML 里，而不是临时改同一个文件。
- 自定义模块集中放置，避免散落在多个官方模块文件中。
- A、B、C、AB、ABC 都从 `weights/pretrained/yolo11n-obb.pt` 起训，不做权重接力。
- AB 和 ABC 是结构组合实验，不是先训 A 再接着训 B/C。
- 无效实验也要登记，不要静默删除，避免后续重复试错。

建议后续代码结构：

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
  yolo11n-obb-c-set-hbs.yaml
  yolo11n-obb-ab-p2-lsk.yaml
  yolo11n-obb-ab-p2-pki-lite.yaml
  yolo11n-obb-abc-p2-pki-geo-plus.yaml
  yolo11n-obb-abc-p2-pki-gra-lite.yaml
  yolo11n-obb-abc-p2-pki-chol-lite.yaml
  yolo11n-obb-abc-p2-pki-set-hbs.yaml

ultralytics/nn/modules/
  remote_obb_blocks.py

experiments/
  dior/
    baseline.yaml
    a_p2.yaml
    b_lsk.yaml
    b_pki_lite.yaml
    b_pki_lite_homews.yaml
    c_dynamic.yaml
    c_dynamic_plus.yaml
    c_dynamic_plus_homews.yaml
    c_gra_lite.yaml
    c_gra_lite_homews.yaml
    c_chol_lite.yaml
    c_chol_lite_homews.yaml
    c_set_hbs.yaml
    c_set_hbs_homews.yaml
    ab_p2_pki_lite.yaml
    ab_p2_pki_lite_homews.yaml
    abc_p2_pki_geo_plus.yaml
    abc_p2_pki_geo_plus_homews.yaml
    abc_p2_pki_gra_lite.yaml
    abc_p2_pki_gra_lite_homews.yaml
    abc_p2_pki_chol_lite.yaml
    abc_p2_pki_chol_lite_homews.yaml
    abc_p2_pki_set_hbs.yaml
    abc_p2_pki_set_hbs_homews.yaml
  <second_dataset>/
    baseline.yaml
    a_p2.yaml
    b_lsk.yaml
    b_pki_lite.yaml
    c_dynamic.yaml
    c_dynamic_plus.yaml
    c_chol_lite.yaml
    ab_p2_pki_lite.yaml
    abc_p2_pki_geo_plus.yaml
    abc_p2_pki_chol_lite.yaml
```

`remote_obb` 表示 remote sensing OBB，即遥感旋转框检测。不要使用 `rsod` 作为目录名，避免和 RSOD 数据集混淆。

当前统一训练入口：

```bash
python scripts/train_obb.py --config experiments/dior/baseline.yaml
```

上述已完成实验配置继续保留。新增 `c_set_hbs.yaml`、`c_set_hbs_homews.yaml`、`abc_p2_pki_set_hbs.yaml` 和 `abc_p2_pki_set_hbs_homews.yaml` 也均为 `status: ready`，当前待训练。新增实验不要再复制出一堆只改一两行的训练脚本，应优先新增或更新 `experiments/<dataset>/<variant>.yaml`。

## 创新点方向候选

优先选择小而清楚、容易写论文动机、容易单独消融的改动。总体路线是：从 CVPR/ICCV/ECCV 等顶会论文中吸收成熟模块思想，参考其官方开源代码，但实际实现要轻量适配 YOLO11n-OBB，避免直接搬入大型 backbone 或复杂依赖。

- 创新点 A：小目标特征增强。当前第一版已落地为 P2/4 OBB 检测分支，配置文件为 `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-a-p2.yaml`，实验配置为 `experiments/dior/a_p2.yaml`。DIOR-R test 结果显示 A-P2 相比 baseline 全尺度 mAP50-95 提升 +0.0116，小目标 mAP50-95 提升 +0.0745，实验有效。
- 创新点 B：遥感上下文注意力。当前已实现为轻量 `SPPFLSK` 模块，文件为 `ultralytics/nn/modules/remote_obb_blocks.py`，结构配置为 `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-b-lsk.yaml`，实验配置为 `experiments/dior/b_lsk.yaml`。该模块在原 SPPF 位置追加 LSK 风格的大核选择上下文注意力。DIOR-R test 结果显示 B-LSK 相比 baseline 全尺度 mAP50-95 下降 -0.0065，小目标 mAP50-95 下降 -0.0032，当前版本无效；无需下载外部论文代码或第三方依赖。
- 创新点 B 第二版：neck 特征融合增强。当前已实现为轻量 `C3k2PKI` 模块，文件为 `ultralytics/nn/modules/remote_obb_blocks.py`，结构配置为 `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-b-pki-lite.yaml`，本地实验配置为 `experiments/dior/b_pki_lite.yaml`，服务器实验配置为 `experiments/dior/b_pki_lite_homews.yaml`。该模块参考 CVPR 2024 PKINet，只在 top-down neck 的 P5->P4、P4->P3 融合块加入多核上下文，不新增检测尺度，也不改 OBB 几何回归。当前 DIOR-R test 结果显示 B-PKI-Lite 相比 baseline 全尺度 mAP50-95 提升 +0.0011，小目标 mAP50-95 提升 +0.0151，比旧 B-LSK 明显更好。
- 创新点 C：已有几何方向版本均未让 ABC 超过 AB。新的优先方向为 C-SET-HBS，参考 CVPR 2025 SET 的 HBS，在训练期通过旋转 GT 前景保护与背景平滑辅助监督改善特征，推理保持 AB；它与 A 的检测尺度、B 的 neck 融合边界清楚，当前配置 ready、待训练。

建议实现顺序：

1. A 已完成第一版训练和评估，结果有效；如需复跑可用 `python scripts/train_obb.py --config experiments/dior/a_p2.yaml --dry-run` 检查配置。
2. B-LSK 已完成第一版训练和评估，但当前无提升；新版 B-PKI-Lite 已完成第一版评估，结果轻微正向，尤其小目标指标比旧 B 更好。
3. A+B-PKI-Lite 已完成训练和评估，当前是 DIOR-R test 最佳结果。
4. C-Dynamic、C-Dynamic-Plus、C-GRA-Lite 和 C-Chol-Lite 均已完成；下一步直接训练 A+B-PKI-Lite+C-SET-HBS，检验训练监督型 C 能否同时提高全尺度和小目标指标。

建议融合顺序：

```text
A
B
C
A + B-PKI-Lite
C-SET-HBS
A + B + C-SET-HBS
```

顶会论文与官方代码入口整理在 `research/top_conference/`。不要把大型第三方仓库直接复制进本仓库；真正实现时，只抽取必要模块并检查许可证、依赖和训练成本。

2024+ 新候选方向和后续实验计划见 `research/top_conference/2024_plus_experiment_plan.md`。当前 A+B-PKI-Lite 是最佳结果；两组旧 ABC 均未超过它。下一组优先训练 A+B-PKI-Lite+C-SET-HBS。注意 YOLO11-OBB 已有 ProbIoU/Gaussian covariance 和周期角度 loss，后续 C 不能把这些已有项换名作为创新。

做消融时，除非某个实验明确研究训练策略，否则要固定训练设置。不要随意改变 `imgsz`、epochs、优化器、数据增强、数据 split，否则很难说明提升来自模型结构本身。

## 本地 Codex + Git + 服务器训练

服务器不需要 Codex 桌面版，也不需要登录 Codex。服务器只负责运行训练命令；本地 Codex 负责维护代码、配置和文档。

- 通用工作流说明：`SERVER_TRAINING.md`，覆盖 Git 首次部署、服务器训练、后续 `git pull` 更新代码、结果回传。
- 无 conda 的 Linux 服务器 venv 部署说明：`SERVER_VENV_SETUP.md`，首次部署需要 `pip install -e .`，后续普通 `git pull` 不需要重复安装。
- 本地和服务器的机器差异放在 `environments/`，当前有 `local.yaml`、`homews.yaml`、`autodl.yaml`、`company5090.yaml`。
- 公司 5090 数据集模板：`ultralytics/cfg/datasets/DIOR-company.yaml`。
- `/home/ws` Linux 数据集配置模板：`ultralytics/cfg/datasets/DIOR-homews.yaml`；AutoDL 模板仍保留为 `ultralytics/cfg/datasets/DIOR-autodl.yaml`。
- 服务器自检脚本：`scripts/check_server_env.py --env homews --require-cuda`。
- 统一训练入口：`scripts/train_obb.py --config experiments/dior/ab_p2_pki_lite_homews.yaml`。
- 续训入口：`scripts/train_obb.py --resume path/to/last.pt`。
- 服务器 90GB 内存时，DIOR-R 训练优先用 `--cache ram`；如果 RAM 不够或换成更大的 DOTA，再退回 `--cache disk`。
- 离线 AMP 检查：`scripts/train_obb.py` 会把 `weights/pretrained/yolo26n.pt` 复制到项目根目录，避免 Ultralytics 在服务器上联网下载。
- 后续本地改完代码后，默认走 `git commit` / `git push`；服务器只做 `git pull`。`pip install -e .` 首次部署执行一次即可，除非新增依赖或包配置变化。
- `weights/` 下的 `.pt` 允许 Git 跟踪，便于服务器训练完提交权重、本地直接拉取；根目录临时 `.pt` 仍忽略。
- `scripts/` 只保留 `train_obb.py`、`evaluate_obb.py`、`check_server_env.py` 三个核心入口，不再保留旧的硬编码训练/预测/切分脚本。

## 命名规范

后续实验建议显式指定 run name，避免 `train10`、`train11` 这种名字混乱：

- `dior_baseline_yolo11n_obb`
- `dior_A_<short_name>`
- `dior_B_<short_name>`
- `dior_C_<short_name>`
- `dior_AB_<short_name>`
- `dior_ABC_<short_name>`
- 第二数据集把 `dior` 替换成对应数据集名，例如 `dota` 或 `hrsc`。

写论文表格前，要单独整理一份实验日志，记录每个实验的模型路径、训练参数、最终指标和验证命令。
