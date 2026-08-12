# 遥感 OBB 模型 YAML 索引

本目录同时保留第三章定稿结构、历史筛选结构和第四章候选结构。文件存在不代表仍需训练；执行状态以 `experiments/chapter4/README.md` 和各数据集 README 为准。

## 第三章定稿结构

| YAML | 定位 |
|---|---|
| `yolo11n-obb-baseline.yaml` | YOLO11n-OBB 受控 baseline |
| `yolo11n-obb-a-p2.yaml` | A：FSPB，新增 P2/stride-4 预测与 PAN 回流 |
| `yolo11n-obb-b-pki-lite.yaml` | B：LPCF，替换两处 top-down 融合块 |
| `yolo11n-obb-ab-p2-pki-lite.yaml` | A+B：FSPC-OBB，第三章最终方法 |

论文写作使用 FSPB/LPCF 正式名称；A-P2、B-PKI-Lite 只作为内部历史名。

## 第三章历史探索

- `yolo11n-obb-b-lsk.yaml`：无效的早期 B，已由 LPCF 替代。
- `yolo11n-obb-c-dynamic*.yaml`、`yolo11n-obb-c-gra-lite.yaml`、`yolo11n-obb-c-chol-lite.yaml`：C 系列单模块探索。
- `yolo11n-obb-abc-*.yaml`、`yolo11n-obb-ab-p2-lsk.yaml`：组合探索。

这些 YAML 为可追溯性保留，不进入第三章主方法，也不是第四章候选。

## 第四章基础结构

- `yolo11n-obb-lsknet-t-baseline.yaml`：LSKNet-T backbone、必要通道适配、原 YOLO11 Neck 和 OBB Head。

LSKNet-T 与适配层属于 baseline 架构选择，不算创新。

## 第四章已完成筛选

- `yolo11n-obb-lsknet-t-oac.yaml`
- `yolo11n-obb-lsknet-t-fdf.yaml`
- `yolo11n-obb-lsknet-t-oac-fdf.yaml`
- `yolo11n-obb-lsknet-t-oac-fdf-blend.yaml`

OAC/FDF 及 Blend 的结果均保留，但组合没有稳定优于两个单模块，不作为当前定稿 C/D。

## 第四章当前候选

- `yolo11n-obb-lsknet-t-fdconv.yaml`：C-v2，FDConv-Lite adapter。
- `yolo11n-obb-lsknet-t-fdconv-fdf.yaml`：C+D，FDConv-Lite + FDF。

两者目前只完成代码、初始化和 seed 42 配置，尚无训练结论。结果成立后再生成三 seed 与第二数据集正式配置。

## 维护规则

- 不创建与 baseline 结构完全相同、仅改文件名的 A/B/C YAML。
- 新 YAML 必须在对应实验 README 中登记改动位置、初始化权重、训练协议和状态。
- 历史 YAML 不删除，但必须避免使用“当前候选”一类无时间边界的描述。
