# DIOR-R 同划分轻量方法对比

> 状态：旧 `18770/2346/2347` 划分计划，现已归档。EI 小论文的 DIOR-R 主实验已切换到 `experiments/dior_official/` 的官方划分；本目录现有配置不得直接进入官方划分主表。如需训练 YOLOv8n-OBB、YOLO26n-OBB 等外部基线，必须另建指向 `DIOR-official*.yaml` 的配置。

本目录用于补充论文中的近期轻量 OBB 方法对比。所有候选模型必须在本项目自己的 DIOR-R `train/val/test` 划分上重新训练和评估，不能直接下载其他论文在官方 DIOR-R 划分上训练的权重后测试。

## 为什么必须重新训练

本项目使用 18770/2346/2347 的第三方 DIOR-R 划分，而公开论文通常使用官方 5862/5863/11738 划分。两个划分的图像集合不一致，公开权重的训练集可能包含本项目测试图像，直接评估会产生数据泄漏；同时，公开论文报告值也不能与本项目结果直接横向比较。

公平流程统一为：

```text
官方通用 OBB 预训练权重
  -> 本项目 DIOR-R train 训练
  -> 本项目 DIOR-R val 选择 best.pt
  -> 本项目 DIOR-R test 最终评估
```

## 入选方法

| 方法 | 年份 | DIOR-R 20 类参数量 | 640 GFLOPs | 初始化 | 作用 |
|---|---:|---:|---:|---|---|
| YOLOv8n-OBB | 2023 | 3,086,415 | 8.46 | 官方 DOTA OBB 权重 | 经典 nano OBB 参照 |
| YOLO11n-OBB | 2024 | 2,657,623 | 6.6 | 官方 DOTA OBB 权重 | 本文 baseline |
| YOLO26n-OBB | 2026 | 2,654,934 | 6.31 | 官方 DOTA OBB 权重 | 近期 nano OBB 参照 |
| A-P2 + B-PKI-Lite | 本文 | 2,740,390 | 10.7 | 官方 YOLO11n-OBB 权重 | 本文方法 |

参数量相对本文 AB：YOLOv8n-OBB 为 `+12.63%`，YOLO26n-OBB 为 `-3.12%`。三者均属于约 2.7M--3.1M 参数的 nano 级模型。

YOLO12n-OBB 暂不进入主对比：其结构参数量接近，但官方没有发布 OBB 预训练权重。若从随机初始化或检测权重训练，会与其余方法的 DOTA OBB 初始化不一致。YOSDet 等论文若没有可核验的官方源码，也不根据论文描述自行复刻，以免比较对象偏离原方法。

## 可直接引用的近协议结果

截至 2026-07-20，尚未检索到同行评审论文明确使用与本项目完全相同的 Kaggle `18770/2346/2347` 划分。该转换数据包由 Mridankan Mandal 于 2025 年发布，公开页面目前也没有配套 benchmark 代码或论文结果。

目前最接近的是 Sensors 2025 的 MS-YOLOv11：同为 Ultralytics YOLO-OBB、20 类 DIOR-R、`imgsz=640` 和约 2.8M 参数，但采用 23190 张图像的 60/20/20 随机划分、batch 16、300 epochs。其 baseline 与本项目 baseline 的结果接近，因此可作为“作者协议报告值”补充，而不能标成完全同协议复现。

| 方法 | Params | mAP50 | mAP50-95 | 协议 |
|---|---:|---:|---:|---|
| YOLOv8-OBB | 未报告 | 84.96 | 未报告 | MS-YOLOv11 论文协议 |
| YOLO11-OBB | 2,802,647 | 85.75 | 66.66 | MS-YOLOv11 论文协议 |
| MS-YOLOv11 | 2,865,383 | 88.33 | 70.90 | MS-YOLOv11 论文协议 |
| YOLO11n-OBB baseline | 2,657,623 | 85.88 | 68.74 | 本项目划分，seed 42 |
| A-P2 + B-PKI-Lite | 2,740,390 | 88.59 | 71.98 | 本项目划分，seed 42 |

论文来源：Liu et al., *MS-YOLOv11: A Wavelet-Enhanced Multi-Scale Network for Small Object Detection in Remote Sensing Images*, Sensors 2025, 25(19), 6008, DOI `10.3390/s25196008`，https://www.mdpi.com/1424-8220/25/19/6008 。

注意：该论文还报告 `mAP(small)=84.21`，虽文字上采用面积小于 32x32 的定义，但其结果与本项目小目标评估差异异常大，且未公开可核验评估代码，因此不把该数值与本项目小目标 mAP50 直接并列。论文正文建议只引用其全尺度 mAP50/mAP50-95。

## 一键训练

本地 Windows：

```powershell
conda run -n yololuck python scripts/train_obb.py --config experiments/dior/comparisons/yolov8n_obb.yaml
conda run -n yololuck python scripts/train_obb.py --config experiments/dior/comparisons/yolo26n_obb.yaml
```

`/home/ws` 服务器（1 号 GPU、自动 batch、内存缓存）：

```bash
# .pt 不进入 Git；首次运行先下载两份官方 OBB 权重
python -c "from ultralytics import YOLO; YOLO('weights/pretrained/yolov8n-obb.pt'); YOLO('weights/pretrained/yolo26n-obb.pt')"

python scripts/train_obb.py --config experiments/dior/comparisons/yolov8n_obb_homews.yaml
python scripts/train_obb.py --config experiments/dior/comparisons/yolo26n_obb_homews.yaml
```

## 统一评估

训练完成后分别执行：

```powershell
conda run -n yololuck python scripts/evaluate_obb.py --model runs/obb/dior_compare_yolov8n_obb/weights/best.pt --data DIOR.yaml --split test --mode both
conda run -n yololuck python scripts/evaluate_obb.py --model runs/obb/dior_compare_yolo26n_obb/weights/best.pt --data DIOR.yaml --split test --mode both
```

最终表格同时报告 Params、GFLOPs、全尺度 mAP50/mAP50-95 和项目既定协议下的小目标 mAP50/mAP50-95。训练完成前不预填结果。

时间成本受限时，只需在本项目划分上补跑 YOLOv8n-OBB 和 YOLO26n-OBB；MS-YOLOv11 使用上表作者报告值并加协议脚注，不再自行复现。
