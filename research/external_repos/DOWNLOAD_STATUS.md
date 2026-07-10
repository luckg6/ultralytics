# 外部源码下载状态

记录日期：2026-07-10

这个文件专门记录第三方论文源码的本地下载状态。`research/external_repos/` 默认被 Git 忽略，但本文件会随仓库保留，便于后续在服务器或本地补齐源码。

## 已成功下载

| 项目 | 本地目录 | 当前状态 |
|---|---|---|
| PKINet | `research/external_repos/PKINet` | 已浅克隆 |
| GRA | `research/external_repos/GRA` | 已浅克隆 |
| FDConv | `research/external_repos/FDConv` | 已浅克隆 |
| GauCho | `research/external_repos/GauCho` | 已浅克隆 |
| YOLOv10 | `research/external_repos/yolov10` | 已浅克隆 |

## 本次未成功下载

| 项目 | 目标目录 | 推荐地址 | 失败原因 | 后续处理 |
|---|---|---|---|---|
| FreqFusion | `research/external_repos/FreqFusion` | `https://github.com/Linwei-Chen/FreqFusion` | `git clone` 过程中网络超时，半成品目录已清理 | 后续重试；也可尝试备用地址 `https://github.com/ying-fu/FreqFusion` |
| CANConv | `research/external_repos/CANConv` | `https://github.com/Duanyll/CANConv` | 访问 GitHub 超时 | 后续重试，或手动下载 zip 解压到目标目录 |

## 重试命令

```bash
git clone --depth 1 https://github.com/Linwei-Chen/FreqFusion research/external_repos/FreqFusion
git clone --depth 1 https://github.com/ying-fu/FreqFusion research/external_repos/FreqFusion
git clone --depth 1 https://github.com/Duanyll/CANConv research/external_repos/CANConv
```

如果手动下载 zip，解压后的目录名请改成上表的目标目录名，方便后续脚本和文档引用。
