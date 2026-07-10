# 外部论文源码临时目录

这个目录用于临时放置第三方论文官方源码，方便本地阅读和抽取必要模块。

注意：

- 这里的第三方源码默认不提交到本仓库。
- 不要直接把完整 MMDetection/MMRotate/MMCV 工程并入主项目。
- 真正落地到 YOLO11n-OBB 时，只抽取必要模块思想，放到项目自己的模块文件和实验配置中。

建议下载命令：

```bash
git clone --depth 1 https://github.com/PKINet/PKINet research/external_repos/PKINet
git clone --depth 1 https://github.com/wangjiangshan0725/GRA research/external_repos/GRA
git clone --depth 1 https://github.com/Linwei-Chen/FreqFusion research/external_repos/FreqFusion
git clone --depth 1 https://github.com/Linwei-Chen/FDConv research/external_repos/FDConv
git clone --depth 1 https://github.com/jhlmarques/GauCho research/external_repos/GauCho
git clone --depth 1 https://github.com/duanyll/CANConv research/external_repos/CANConv
git clone --depth 1 https://github.com/THU-MIG/yolov10 research/external_repos/yolov10
```

## 当前本地下载状态

截至 2026-07-10，本地已成功浅克隆：

- `research/external_repos/PKINet`
- `research/external_repos/GRA`
- `research/external_repos/FDConv`
- `research/external_repos/GauCho`
- `research/external_repos/yolov10`

本次未成功下载：

- `FreqFusion`：clone 过程中网络超时，残留半成品目录已清理。可手动重试 `https://github.com/Linwei-Chen/FreqFusion`，或备用入口 `https://github.com/ying-fu/FreqFusion`。
- `CANConv`：访问 GitHub 时超时。可手动重试 `https://github.com/Duanyll/CANConv`。

更完整的状态表和重试命令见 `research/external_repos/DOWNLOAD_STATUS.md`。
