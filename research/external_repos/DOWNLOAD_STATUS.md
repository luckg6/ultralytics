# 外部源码与权重材料状态

更新日期：2026-08-12

本文件记录论文实验候选方法的外部源码和预训练权重准备状态。`research/external_repos/` 默认不随 Git 提交完整源码；本文件保留材料来源、当前位置和后续处理状态，便于本地与服务器复现。

## 已成功准备

| 项目 | 本地路径 | 当前状态 |
|---|---|---|
| PKINet | `research/external_repos/PKINet` | 已克隆；CVPR 2024 remote sensing detection backbone/reference |
| GRA | `research/external_repos/GRA` | 已克隆；ECCV 2024 oriented object detection orientation-aware module/reference |
| FreqFusion | `research/external_repos/FreqFusion` | 用户已手动补齐；已检查 `README.md` 和 `FreqFusion.py` 存在 |
| FDConv | `research/external_repos/FDConv` | 已克隆；CVPR 2025 frequency dynamic convolution/reference |
| GauCho | `research/external_repos/GauCho` | 已克隆；OBB geometry representation/reference |
| YOLOv10 | `research/external_repos/yolov10` | 已克隆；效率/assignment 参考，不作为第四章主创新 |
| LSKNet | `research/external_repos/LSKNet` | 用户已手动补齐，已检查 `README.md`、`mmrotate/models/backbones/lsknet.py`、`configs/lsknet/lsk_t_fpn_1x_dota_le90.py` 存在 |
| LSKNet-T DOTA checkpoint | `weights/pretrained/lsknet/lsk_t_fpn_1x_dota_le90_20230206-3ccee254.pth` | 用户已手动补齐，已在 `yololuck` 环境读取成功；包含 478 个 `backbone.*` 权重 key |
| LSKNet-T ImageNet backbone checkpoint（备用） | `weights/pretrained/lsknet/lsk_t_backbone.pth.tar` | 用户已手动补齐，已在 `yololuck` 环境读取成功；作为 DOTA 权重不可用时的备用初始化 |

## 仍未成功准备

| 项目 | 目标目录 | 推荐地址 | 当前问题 | 后续处理 |
|---|---|---|---|---|
| CANConv | `research/external_repos/CANConv` | `https://github.com/duanyll/CANConv` | 2026-07-29 再次 `git clone --depth 1` 超时；本地可能只残留不完整 `.git` 目录，不能视为源码已齐 | 低优先级。若后续使用，建议手动下载 zip 后解压到目标目录 |

## 可重试命令

```bash
git clone --depth 1 https://github.com/duanyll/CANConv research/external_repos/CANConv
```

如果手动下载 zip，解压后的目录名请改成上表的目标目录名。若目录中只有 `.git` 而没有 `README.md` 或源码文件，说明之前 clone 未完成，需要先删除该目录再重新解压。
