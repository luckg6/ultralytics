# 训练后 Checkpoint 索引

整理日期：2026-08-12

本目录是项目中训练后可用 `best.pt` 的唯一长期保留位置。每个目录尽量同时保存 `args.yaml`、`results.csv` 和 `results.png`；`last.pt`、临时验证输出和淘汰筛选权重不保留。

## 目录结构

```text
weights/checkpoints/
  chapter3/
    dior_official/seed42/{baseline,fspb,lpcf,fspc_obb}/
    dior_811/seed42/{baseline,fspb,lpcf,fspc_obb}/
    hrsid/seed42/{baseline,fspb,lpcf,fspc_obb}/
    hrsid/seed3407/{baseline,fspb,lpcf,fspc_obb}/
    dior_official_comparisons/seed42/{yolov8n_obb,yolo26n_obb}/
  chapter4/
    dior_official/{seed42,seed3407,seed2026}/{baseline,fdf}/
```

## 保留边界

- `chapter3/dior_official`：第三章第一主数据集的可用本地 seed 42 checkpoint。
- `chapter3/dior_811`：论文 alternate-split robustness 所需的四组 checkpoint。
- `chapter3/hrsid`：本地现有的两套完整四组消融 checkpoint。seed 42 是首轮结果，seed 3407 是完整理想排序结果。
- `chapter3/dior_official_comparisons`：同协议 YOLOv8n-OBB 与 YOLO26n-OBB 对比。
- `chapter4/dior_official`：当前新组合评估仍需复用的 LSKNet-T baseline 与 FDF 三 seed checkpoint。

当前论文稳定性表还包含服务器汇总的其他 seed 数据，但相应完整训练权重并未全部复制到本机。本目录只声明实际存在并完成校验的 checkpoint，不用缺失权重反推或拼接结果。

## 已清理内容

- 第三章失败 C/ABC 和旧 B-LSK checkpoint；
- UCAS-AOD、VEDAI、SSDD-RBox、HRSC2016 筛选 checkpoint；
- 第四章已淘汰的 OAC、OAC+FDF 和 Blend checkpoint；
- 所有 `last.pt`、临时 `val*` 目录和可重新生成的评估图片。

数值结论仍保存在论文 PDF、实验 README 和原始评估 Markdown 中。需要复跑已清理的历史模型时，应从对应 YAML 和预训练权重重新训练。

## Git 规则

本目录中的训练后 `.pt` 默认被 git 忽略，仅本地保存。`weights/pretrained/` 中服务器直接训练所需的预训练和混合初始化权重仍允许随 Git 同步。
