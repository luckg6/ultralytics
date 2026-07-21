# DIOR-R 官方划分复现实验

本目录用于在 DIOR/DIOR-R 的官方数据划分上重新训练 baseline、A-P2、B-PKI-Lite 和 A+B-PKI-Lite。原有 `C:/E/datasets/YOLODIOR-R/` 及其 8:1:1 实验结果不覆盖、不删除。

## 数据划分

| 子集 | 图像编号 | 图像数 | 用途 |
|---|---:|---:|---|
| train | `00001`-`05862` | 5,862 | 参数训练 |
| val | `05863`-`11725` | 5,863 | 选择 `best.pt` |
| test | `11726`-`23463` | 11,738 | 最终一次性报告 |

三份列表与公开 `ImageSets/Main/{train,val,test}.txt` 的 Git blob SHA-1 完全一致。来源为 Hugging Face 数据集 `Qingyun/lmmrotate-sft-data` 中按 MMRotate 官方说明整理的 DIOR 文件；列表内容也与公开的 DIOR trainval/test 图像归档边界一致。

本地数据已经由以下命令从现有 YOLO OBB 标注重排生成：

```powershell
python scripts/prepare_dior_r_official_split.py `
  --source C:/E/datasets/YOLODIOR-R `
  --output C:/E/datasets/YOLODIOR-R-official `
  --mode hardlink
```

`hardlink` 只用于节省本机磁盘；压缩或复制到服务器后仍是普通独立文件。

## 服务器位置

把完整数据目录放到：

```text
/home/ws/datasets/YOLODIOR-R-official/
├── train/images, train/labels
├── val/images, val/labels
├── test/images, test/labels
└── split_manifest.json
```

服务器数据 YAML 已固定指向该路径。服务器训练配置统一为 `device=1`、`batch=-1`、`cache=ram`；本地配置为 `device=0`、`batch=4`、`cache=disk`。四组实验均使用 `seed=42`、`epochs=100`、`imgsz=640`，并分别从同一个 `weights/pretrained/yolo11n-obb.pt` 初始化。

## 训练命令

建议先跑 baseline 和 AB；确认 AB 正向后，再补 A、B 两项消融。

```bash
python scripts/train_obb.py --config experiments/dior_official/baseline_homews.yaml
python scripts/train_obb.py --config experiments/dior_official/ab_p2_pki_lite_homews.yaml
python scripts/train_obb.py --config experiments/dior_official/a_p2_homews.yaml
python scripts/train_obb.py --config experiments/dior_official/b_pki_lite_homews.yaml
```

本机运行时去掉文件名中的 `_homews` 即可。

## 最终评估

训练过程中只根据 `val` 选择 `best.pt`。四组都确定后，再在 `test` 上统一运行：

```bash
python scripts/evaluate_obb.py --model runs/obb/dior_official_AB_p2_pki_lite/weights/best.pt --data ultralytics/cfg/datasets/DIOR-official-homews.yaml --split test --mode both --device 1
```

论文中应明确写作“采用 DIOR 官方 train/val/test 划分”，不可再把原 Kaggle 8:1:1 结果与官方协议论文放入同一张公平对比表。
