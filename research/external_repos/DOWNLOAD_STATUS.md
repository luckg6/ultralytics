# 外部源码与权重材料状态

记录日期：2026-07-28

本文件记录论文实验候选方法的外部源码和预训练权重准备状态。`research/external_repos/` 默认不随 Git 提交完整源码；本文件保留材料来源、当前位置和后续处理状态，便于本地与服务器复现。

## 已成功准备

| 项目 | 本地路径 | 当前状态 |
|---|---|---|
| PKINet | `research/external_repos/PKINet` | 已克隆 |
| GRA | `research/external_repos/GRA` | 已克隆 |
| FDConv | `research/external_repos/FDConv` | 已克隆 |
| GauCho | `research/external_repos/GauCho` | 已克隆 |
| YOLOv10 | `research/external_repos/yolov10` | 已克隆 |
| LSKNet | `research/external_repos/LSKNet` | 用户已手动补齐，已检查 `README.md`、`mmrotate/models/backbones/lsknet.py`、`configs/lsknet/lsk_t_fpn_1x_dota_le90.py` 存在 |
| LSKNet-T DOTA checkpoint | `weights/pretrained/lsknet/lsk_t_fpn_1x_dota_le90_20230206-3ccee254.pth` | 用户已手动补齐，已在 `yololuck` 环境读取成功；包含 478 个 `backbone.*` 权重 key |
| LSKNet-T ImageNet backbone checkpoint（备用） | `weights/pretrained/lsknet/lsk_t_backbone.pth.tar` | 用户已手动补齐，已在 `yololuck` 环境读取成功；作为 DOTA 权重不可用时的备用初始化 |

## 仍未成功准备

| 项目 | 目标目录 | 推荐地址 | 当前问题 | 后续处理 |
|---|---|---|---|---|
| FreqFusion | `research/external_repos/FreqFusion` | `https://github.com/Linwei-Chen/FreqFusion` | `git clone` 过程网络超时 | 后续可重试，也可尝试备用地址 `https://github.com/ying-fu/FreqFusion` |
| CANConv | `research/external_repos/CANConv` | `https://github.com/Duanyll/CANConv` | 访问 GitHub 超时 | 后续可重试，或手动下载 zip 解压到目标目录 |

## 可重试命令

```bash
git clone --depth 1 https://github.com/Linwei-Chen/FreqFusion research/external_repos/FreqFusion
git clone --depth 1 https://github.com/ying-fu/FreqFusion research/external_repos/FreqFusion
git clone --depth 1 https://github.com/Duanyll/CANConv research/external_repos/CANConv
```

如果手动下载 zip，解压后的目录名请改成上表的目标目录名，方便后续脚本和文档引用。
