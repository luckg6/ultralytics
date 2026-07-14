# remote_obb 模型结构配置

这个目录用于管理遥感影像小目标 OBB 旋转框检测的 YOLO11n 结构变体。

## 当前文件

- `yolo11n-obb-baseline.yaml`：YOLO11n-OBB baseline 结构，复制自官方 `yolo11-obb.yaml`，显式作为本课题 baseline 配置使用。
- `yolo11n-obb-a-p2.yaml`：实验 A，在 P3/P4/P5 的 OBB head 基础上新增 P2/4 小目标检测分支。
- `yolo11n-obb-b-lsk.yaml`：实验 B，在原 SPPF 位置使用轻量 `SPPFLSK` 上下文注意力模块，保持 OBB(P3/P4/P5) head 不变，用于单独消融遥感上下文建模。
- `yolo11n-obb-b-pki-lite.yaml`：实验 B 第二版，在 top-down neck 的 P5->P4、P4->P3 融合块使用轻量 `C3k2PKI`，用于替代效果不佳的 B-LSK。
- `yolo11n-obb-c-dynamic.yaml`：实验 C，在 OBB head 的 P3/P4/P5 输出融合层使用轻量 `C3k2Geo` 方向几何感知模块，用于单独消融旋转目标几何适应。
- `yolo11n-obb-c-dynamic-plus.yaml`：实验 C 加强版，在相同 OBB head 位置使用更强的 `C3k2GeoPlus`，不覆盖原 C-Dynamic，用于复验更强几何适应模块。
- `yolo11n-obb-c-gra-lite.yaml`：实验 C 新候选，参考 ECCV 2024 GRA，在 OBB head 的 P3/P4/P5 输出融合层使用轻量 `C3k2GRA` 方向路由模块。
- `yolo11n-obb-ab-p2-pki-lite.yaml`：A + 新版 B-PKI-Lite，保留 P2 检测分支，同时在原 top-down neck 的 P5->P4、P4->P3 融合块使用 `C3k2PKI`。
- `yolo11n-obb-abc-p2-pki-geo-plus.yaml`：A + B-PKI-Lite + C-Dynamic-Plus，已完成训练和评估，强于 baseline 但低于 A+B-PKI-Lite。
- `yolo11n-obb-abc-p2-pki-gra-lite.yaml`：A + B-PKI-Lite + C-GRA-Lite，待训练，用于验证新版 C 是否能和 A+B 形成更强互补。

## 后续计划

旧计划中尚未优先训练的 YAML：

- `yolo11n-obb-ab-p2-lsk.yaml`：A + 旧版 B-LSK，当前不建议优先训练。
- `yolo11n-obb-abc-p2-lsk-dynamic.yaml`：A + B + C。

不要创建和 baseline 完全相同但命名为 A/B/C 的 YAML，避免后续误跑假改进实验。
