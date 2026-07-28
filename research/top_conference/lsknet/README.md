# LSKNet

## 基本信息

- 论文：Large Selective Kernel Network for Remote Sensing Object Detection
- 会议：ICCV 2023
- 论文页面：https://openaccess.thecvf.com/content/ICCV2023/html/Li_Large_Selective_Kernel_Network_for_Remote_Sensing_Object_Detection_ICCV_2023_paper.html
- PDF：https://openaccess.thecvf.com/content/ICCV2023/papers/Li_Large_Selective_Kernel_Network_for_Remote_Sensing_Object_Detection_ICCV_2023_paper.pdf
- 官方代码：https://github.com/zcablii/LSKNet

## 在本项目中的定位

LSKNet 面向遥感目标检测提出大选择核机制，强调遥感目标需要根据场景动态选择不同范围的上下文信息。第四章采用 LSKNet-T 作为新的 backbone baseline，目的是把研究切入点从第三章的 Neck/Head 细尺度传递，推进到 Backbone 特征提取阶段的自适应感受野与长程上下文建模。

注意：LSKNet-T backbone 替换和必要通道适配只作为第四章基础架构，不作为创新点。第四章创新点只来自后续 C、D 两个模块。

## 本地材料状态

用户已手动补齐并通过本地核验：

| 材料 | 本地路径 | 状态 |
|---|---|---|
| LSKNet 源码 | `research/external_repos/LSKNet/` | 已确认 `README.md`、`mmrotate/models/backbones/lsknet.py`、`configs/lsknet/lsk_t_fpn_1x_dota_le90.py` 存在 |
| DOTA LSKNet-T + Oriented R-CNN checkpoint | `weights/pretrained/lsknet/lsk_t_fpn_1x_dota_le90_20230206-3ccee254.pth` | 已读取成功 |
| ImageNet LSKNet-T backbone checkpoint（备用） | `weights/pretrained/lsknet/lsk_t_backbone.pth.tar` | 已读取成功，备用 |

## 官方 LSKNet-T 核验摘要

- 官方配置：`embed_dims=[32, 64, 160, 256]`，`depths=[3, 3, 5, 2]`。
- DOTA checkpoint 文件大小：84,128,596 bytes。
- DOTA checkpoint 顶层 key：`meta`、`state_dict`。
- DOTA checkpoint `state_dict` 共 508 个 key，其中 `backbone.*` 共 478 个 key。
- DOTA checkpoint 总 tensor 参数量：21,002,742；可提取的 `backbone.*` 参数量：3,997,644。
- ImageNet checkpoint 文件大小：68,626,267 bytes；为纯 backbone 风格 key，无 `backbone.` 前缀；tensor 参数量：4,254,644。

## 当前实现状态

已完成第一阶段 baseline 的结构与初始化：

- 模块实现：`ultralytics/nn/modules/remote_obb_blocks.py` 中的 `LSKNetT`。
- 模型 YAML：`ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml`。
- 初始化脚本：`scripts/prepare_lsknet_yolo_init.py`。
- 初始化报告：`experiments/chapter4/lsknet_t_baseline_init_report.md`。
- 本地训练配置：`experiments/chapter4/lsknet_t_baseline_dior_official.yaml`。
- `/home/ws` 训练配置：`experiments/chapter4/lsknet_t_baseline_dior_official_homews.yaml`。

当前 baseline 结构为：

`LSKNet-T Backbone + P3/P4 1x1 channel adapters + original YOLO11n-OBB SPPF/C2PSA + original YOLO11n-OBB PAN neck + original YOLO11n-OBB OBB head`

它不包含第三章 FSPB、LPCF 或 P2 OBB 检测分支。

## 初始化核验结果

使用 `scripts/prepare_lsknet_yolo_init.py` 生成混合初始化权重：

- 输出权重：`weights/pretrained/lsknet/yolo11n_obb_lsknet_t_hybrid_init.pt`。
- LSKNet-T 输出：
  - C2：`(1, 32, 160, 160)`
  - C3：`(1, 64, 80, 80)`
  - C4：`(1, 160, 40, 40)`
  - C5：`(1, 256, 20, 20)`
- DOTA backbone 权重加载：478/478。
- YOLO11n-OBB neck/head 权重加载：304/355。
- YOLO 未加载项集中在 `model.23.cv3.*` 分类分支，原因是源权重类别头与当前 YAML 默认类别数/通道不匹配；训练到 DIOR-R 时分类分支本来也会按数据集类别重新初始化。
- 随机初始化模块：
  - `model.5.*`：P3 adapter；
  - `model.6.*`：P4 adapter；
  - `model.21.cv3.*`：分类分支。
- 模型规模：376 layers，5,763,985 params，18.9 GFLOPs at 640。

## 使用命令

本地：

```bash
python scripts/prepare_lsknet_yolo_init.py --model ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official.yaml
```

`/home/ws` 服务器：

```bash
python scripts/prepare_lsknet_yolo_init.py --model ultralytics/cfg/models/11/remote_obb/yolo11n-obb-lsknet-t-baseline.yaml
python scripts/train_obb.py --config experiments/chapter4/lsknet_t_baseline_dior_official_homews.yaml
```

## 后续约束

- LSKNet-S 暂不作为第四章主方案，最多保留为后续骨干选择对比项。
- 在 LSKNet-T baseline 的 DIOR-R 单种子训练结果出来之前，不同时设计 C、D。
- 若 baseline 本身明显强于 YOLO11n-OBB，论文中必须把收益归因写清楚：Backbone 更换是基础设定，C、D 才是第四章创新。
- Params、GFLOPs、FPS/latency 和显存占用必须如实记录，不要求一定低于第三章。
