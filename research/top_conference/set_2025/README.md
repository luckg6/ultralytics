# SET / Spectral Enhancement for Tiny Object Detection

- 论文：SET: Spectral Enhancement for Tiny Object Detection
- 会议：CVPR 2025
- 官方论文：https://openaccess.thecvf.com/content/CVPR2025/html/Sun_SET_Spectral_Enhancement_for_Tiny_Object_Detection_CVPR_2025_paper.html
- PDF：https://openaccess.thecvf.com/content/CVPR2025/papers/Sun_SET_Spectral_Enhancement_for_Tiny_Object_Detection_CVPR_2025_paper.pdf
- 官方源码：截至 2026-07-16，论文主页和公开检索均未给出官方代码仓库。

## 本项目采用的部分

本项目只采用论文的 HBS（Hierarchical Background Smoothing）思路，不声称复现完整 SET。论文消融中，HBS 单独将 FCOS 的 AI-TOD AP 从 12.0 提升到 13.9；完整 SET 为 14.2。HBS 是贡献最大的单个组件，并且比需要额外梯度计算的 API 更适合当前 YOLO11n-OBB 主线。

项目实现为 `C-SET-HBS`：

- 根据 OBB GT 生成旋转前景掩码，比原论文的普通框掩码更贴合遥感旋转框任务。
- 前景特征保持不变，只对背景特征执行通道压缩、尺度相关平滑和通道恢复。
- HBS 特征通过共享 OBB head 产生辅助检测监督。
- 验证和推理只使用原 A+B-PKI-Lite 主路径，HBS 不参与推理。
- 通道压缩率固定为论文推荐的 `r=4`，辅助损失权重采用论文推荐的 `lambda=1`。

对应文件：

- Head：`ultralytics/nn/modules/head.py` 中的 `OBBSETHBS`
- Loss：`ultralytics/utils/loss.py` 中的 SET-HBS 辅助路径
- 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-abc-p2-pki-set-hbs.yaml`
- 单独 C 模型：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-c-set-hbs.yaml`
- 单独 C 配置：`experiments/dior/c_set_hbs.yaml`、`experiments/dior/c_set_hbs_homews.yaml`
- 本地配置：`experiments/dior/abc_p2_pki_set_hbs.yaml`
- `/home/ws` 配置：`experiments/dior/abc_p2_pki_set_hbs_homews.yaml`
