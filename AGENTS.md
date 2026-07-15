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

## 当前 C-Chol-Lite 实验状态

- C-Chol-Lite 已完成代码实现和基础检查，当前待训练和评估。
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
- 本地训练命令：
  - `python scripts/train_obb.py --config experiments/dior/c_chol_lite.yaml --env local`
- `/home/ws` 服务器训练命令：
  - `python scripts/train_obb.py --config experiments/dior/c_chol_lite_homews.yaml`
- 后续组合：A+B-PKI-Lite+C-Chol-Lite 配置也已 ready：
  - 本地配置：`experiments/dior/abc_p2_pki_chol_lite.yaml`
  - `/home/ws` 配置：`experiments/dior/abc_p2_pki_chol_lite_homews.yaml`
  - 模型结构：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-abc-p2-pki-chol-lite.yaml`
  - 构建检查参数量：2,897,906。
  - 从 `weights/pretrained/yolo11n-obb.pt` 可迁移 297/777 项权重。
  - dummy forward 和训练态 5 项 loss 正常。
- 建议：先训练单独 C-Chol-Lite；如果它优于 C-Dynamic-Plus，再训练 A+B-PKI-Lite+C-Chol-Lite。

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
- 最终论文表格建议统一使用同一个 split，例如都用 `split='test'`，确保所有模型公平比较。
- `cache='disk'` 会在 images 文件夹下生成 `.npy` 缓存文件，统计原始图片数量时不要把 `.npy` 算进去。
- 第二个数据集候选：
  - DOTA-v1.0：最适合遥感 OBB 检测论文，但训练成本更高。
  - HRSC2016：船舶旋转框数据集，体量更轻，适合作为第二数据集补实验。

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
python scripts/evaluate_obb.py --model path/to/best.pt --data DOTAv1.yaml --split test --mode all
python scripts/evaluate_obb.py --model path/to/best.pt --data DIOR.yaml --mode small
```

## 实验矩阵

每个数据集上建议做 1 个 baseline 加 5 个改进实验：

1. Baseline：YOLO11n-OBB。
2. 创新点 A：P2/4 小目标检测分支，当前 DIOR-R test 已验证有效。
3. 创新点 B：轻量 `SPPFLSK` 遥感上下文注意力，当前已评估但未提升。
4. 创新点 C：C-Dynamic、C-Dynamic-Plus 已完成但提升较弱；C-GRA-Lite 已评估但弱于 C-Plus；C-Chol-Lite 已实现待训练。
5. 双创新点融合：A+B-PKI-Lite 已完成并取得当前最佳结果；如需补充，可继续做 A+C。
6. 三创新点融合：A+B-PKI-Lite+C-Plus 已完成，强于 baseline 但低于 A+B-PKI-Lite；A+B-PKI-Lite+C-GRA-Lite 暂不优先；A+B-PKI-Lite+C-Chol-Lite 已 ready，等待 C-Chol-Lite 单点结果后决定是否训练。

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
  yolo11n-obb-ab-p2-lsk.yaml
  yolo11n-obb-ab-p2-pki-lite.yaml
  yolo11n-obb-abc-p2-pki-geo-plus.yaml
  yolo11n-obb-abc-p2-pki-gra-lite.yaml
  yolo11n-obb-abc-p2-pki-chol-lite.yaml

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
    ab_p2_pki_lite.yaml
    ab_p2_pki_lite_homews.yaml
    abc_p2_pki_geo_plus.yaml
    abc_p2_pki_geo_plus_homews.yaml
    abc_p2_pki_gra_lite.yaml
    abc_p2_pki_gra_lite_homews.yaml
    abc_p2_pki_chol_lite.yaml
    abc_p2_pki_chol_lite_homews.yaml
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

`experiments/dior/baseline.yaml`、`experiments/dior/a_p2.yaml`、`experiments/dior/b_lsk.yaml`、`experiments/dior/b_pki_lite.yaml`、`experiments/dior/b_pki_lite_homews.yaml`、`experiments/dior/c_dynamic.yaml`、`experiments/dior/c_dynamic_plus.yaml`、`experiments/dior/c_dynamic_plus_homews.yaml`、`experiments/dior/c_gra_lite.yaml`、`experiments/dior/c_gra_lite_homews.yaml`、`experiments/dior/c_chol_lite.yaml`、`experiments/dior/c_chol_lite_homews.yaml`、`experiments/dior/ab_p2_pki_lite.yaml`、`experiments/dior/ab_p2_pki_lite_homews.yaml`、`experiments/dior/abc_p2_pki_geo_plus.yaml`、`experiments/dior/abc_p2_pki_geo_plus_homews.yaml`、`experiments/dior/abc_p2_pki_gra_lite.yaml`、`experiments/dior/abc_p2_pki_gra_lite_homews.yaml`、`experiments/dior/abc_p2_pki_chol_lite.yaml` 和 `experiments/dior/abc_p2_pki_chol_lite_homews.yaml` 当前为 `status: ready`，其中 A-P2、B-LSK、B-PKI-Lite、C-Dynamic、C-Dynamic-Plus、C-GRA-Lite、A+B-PKI-Lite 和 A+B-PKI-Lite+C-Plus 均已完成训练和评估；C-Chol-Lite 待训练。新增实验不要再复制出一堆只改一两行的训练脚本，应优先新增或更新 `experiments/<dataset>/<variant>.yaml`。

## 创新点方向候选

优先选择小而清楚、容易写论文动机、容易单独消融的改动。总体路线是：从 CVPR/ICCV/ECCV 等顶会论文中吸收成熟模块思想，参考其官方开源代码，但实际实现要轻量适配 YOLO11n-OBB，避免直接搬入大型 backbone 或复杂依赖。

- 创新点 A：小目标特征增强。当前第一版已落地为 P2/4 OBB 检测分支，配置文件为 `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-a-p2.yaml`，实验配置为 `experiments/dior/a_p2.yaml`。DIOR-R test 结果显示 A-P2 相比 baseline 全尺度 mAP50-95 提升 +0.0116，小目标 mAP50-95 提升 +0.0745，实验有效。
- 创新点 B：遥感上下文注意力。当前已实现为轻量 `SPPFLSK` 模块，文件为 `ultralytics/nn/modules/remote_obb_blocks.py`，结构配置为 `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-b-lsk.yaml`，实验配置为 `experiments/dior/b_lsk.yaml`。该模块在原 SPPF 位置追加 LSK 风格的大核选择上下文注意力。DIOR-R test 结果显示 B-LSK 相比 baseline 全尺度 mAP50-95 下降 -0.0065，小目标 mAP50-95 下降 -0.0032，当前版本无效；无需下载外部论文代码或第三方依赖。
- 创新点 B 第二版：neck 特征融合增强。当前已实现为轻量 `C3k2PKI` 模块，文件为 `ultralytics/nn/modules/remote_obb_blocks.py`，结构配置为 `ultralytics/cfg/models/11/remote_obb/yolo11n-obb-b-pki-lite.yaml`，本地实验配置为 `experiments/dior/b_pki_lite.yaml`，服务器实验配置为 `experiments/dior/b_pki_lite_homews.yaml`。该模块参考 CVPR 2024 PKINet，只在 top-down neck 的 P5->P4、P4->P3 融合块加入多核上下文，不新增检测尺度，也不改 OBB 几何回归。当前 DIOR-R test 结果显示 B-PKI-Lite 相比 baseline 全尺度 mAP50-95 提升 +0.0011，小目标 mAP50-95 提升 +0.0151，比旧 B-LSK 明显更好。
- 创新点 C：旋转目标几何适应。第一版 `C3k2Geo` 和加强版 `C3k2GeoPlus` 都已完成训练和评估，均为轻微正向但不强；A+B-PKI-Lite+C-Plus 也未超过 A+B-PKI-Lite。C-GRA-Lite 已完成训练，小目标略高于 baseline 但弱于 C-Dynamic-Plus。新版 C-Chol-Lite 已实现为 `OBBCholesky` 训练时 Cholesky/SPD 协方差辅助 head，明确避开 YOLO11 已有的 ProbIoU/Gaussian covariance/周期角度 loss；配置为 `experiments/dior/c_chol_lite.yaml` 和 `experiments/dior/c_chol_lite_homews.yaml`，当前待训练。若 C-Chol-Lite 单点优于 C-Dynamic-Plus，再训练 `experiments/dior/abc_p2_pki_chol_lite_homews.yaml`。

建议实现顺序：

1. A 已完成第一版训练和评估，结果有效；如需复跑可用 `python scripts/train_obb.py --config experiments/dior/a_p2.yaml --dry-run` 检查配置。
2. B-LSK 已完成第一版训练和评估，但当前无提升；新版 B-PKI-Lite 已完成第一版评估，结果轻微正向，尤其小目标指标比旧 B 更好。
3. A+B-PKI-Lite 已完成训练和评估，当前是 DIOR-R test 最佳结果。
4. C-Dynamic、C-Dynamic-Plus 和 C-GRA-Lite 均已完成训练和评估，C-Plus 是当前较好的 C 单点但仍不强；A+B-PKI-Lite+C-Plus 已完成并低于 A+B-PKI-Lite。新版 C-Chol-Lite 已 ready，建议先训练单独 C-Chol-Lite，再决定是否训练 A+B-PKI-Lite+C-Chol-Lite。

建议融合顺序：

```text
A
B
C
A + B-PKI-Lite
C-Chol-Lite
A + B + C-Chol-Lite
```

顶会论文与官方代码入口整理在 `research/top_conference/`。不要把大型第三方仓库直接复制进本仓库；真正实现时，只抽取必要模块并检查许可证、依赖和训练成本。

2024+ 新候选方向和后续实验计划见 `research/top_conference/2024_plus_experiment_plan.md`。当前 A+B-PKI-Lite 已在 DIOR-R test 上取得最佳结果；A+B-PKI-Lite+C-Plus 已完成但低于 A+B-PKI-Lite；C-GRA-Lite 已完成但弱于 C-Plus。若继续追求 ABC 超过 AB，下一步优先训练 C-Chol-Lite 单点；如果正向明显，再训练 A+B-PKI-Lite+C-Chol-Lite。注意 YOLO11-OBB 已有 ProbIoU/Gaussian covariance 和周期角度 loss，后续 C 不能把这些已有项换名作为创新。

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
