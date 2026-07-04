# 顶会论文与开源代码参考

这个目录用于沉淀后续 3 个创新点可能参考的顶会论文、官方开源代码和迁移到 YOLO11n-OBB 的计划。

当前不直接把第三方大型代码仓库复制进来，原因是：

- 顶会开源项目通常体量大、依赖复杂，直接放入本仓库会污染实验代码。
- 不同项目许可证不同，正式抽取代码前需要确认许可证兼容性。
- 本论文目标是轻量改进 YOLO11n-OBB，优先抽取必要模块思想，而不是整体替换模型。

## 候选方向

| 目录 | 论文/模块 | 会议 | 对应创新点 | 优先级 |
| --- | --- | --- | --- | --- |
| `efficientdet_bifpn/` | EfficientDet / BiFPN | CVPR 2020 | 小目标多尺度特征融合 | 高 |
| `lsknet/` | Large Selective Kernel Network | ICCV 2023 | 遥感上下文注意力 | 高 |
| `internimage_dcnv3/` | InternImage / DCNv3 | CVPR 2023 | 动态空间采样/几何适应 | 中 |
| `dynamic_head/` | Dynamic Head | CVPR 2021 | 检测头注意力备选 | 中 |

## 建议落地顺序

1. 先实现 P2 head 或轻量加权特征融合，作为创新点 A。
2. 再实现 LSK 类遥感上下文注意力，作为创新点 B。
3. 最后评估 DCNv3 或 Dynamic Head 类模块，作为创新点 C 或备选 C。

