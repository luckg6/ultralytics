# 第四章实验入口

第四章当前第一阶段只实现新的 backbone baseline：

`LSKNet-T Backbone + 必要通道适配层 + 原始 YOLO11 Neck + 原始 YOLO11 OBB Head`

该 baseline 不继承第三章的 FSPB 和 LPCF；LSKNet-T 与通道适配只作为第四章基础架构，不作为创新点。后续 C、D 模块必须在该 baseline 跑通并完成单种子验证后再设计。

## 第一阶段配置

| 环境 | 配置 | 说明 |
|---|---|---|
| 本地 | `experiments/chapter4/lsknet_t_baseline_dior_official.yaml` | `batch=4`、`cache=disk`、`device=0` |
| `/home/ws` | `experiments/chapter4/lsknet_t_baseline_dior_official_homews.yaml` | `batch=-1`、`cache=ram`、`device=1` |

首次训练前先生成混合初始化权重：

```bash
python scripts/prepare_lsknet_yolo_init.py --model ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml
```

然后开始训练：

```bash
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official.yaml
```

服务器上使用：

```bash
python scripts/prepare_lsknet_yolo_init.py --model ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews.yaml
```

## 第一阶段必须记录

- LSKNet-T 四个 stage 输出：stride `4/8/16/32`，通道 `32/64/160/256`。
- DOTA checkpoint 的 `backbone.*` 权重加载成功率。
- YOLO11n-OBB neck/head 兼容权重加载情况。
- 随机初始化层列表，尤其是 `P3/P4` 通道适配层。
- Params、GFLOPs。
- DIOR-R official split 单种子完整训练结果。
- 与第三章 YOLO11n-OBB baseline 的同协议对比。
