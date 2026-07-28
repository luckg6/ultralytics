# 硕士论文第三章与第四章方案共识（供 Codex 执行）

## 0. Codex 核验记录（2026-07-28）

### 0.1 已核实无误的数据

本文档第 2.4 节列出的第三章单次结果和三随机种子均值，已与 `paper/ippr2026/main.tex`、`paper/ippr2026/main.pdf`、根目录 `README.md`、`experiments/dior_official/README.md` 和 `experiments/hrsid/README.md` 逐项核对，数值一致。

当前第三章正式口径为：

- 方法名：FSPC-OBB；
- A：FSPB，Fine-Scale Preservation Branch；
- B：LPCF，Lightweight Poly-Kernel Context Fusion；
- 数据集：DIOR-R official 与 HRSID-derived OBB；
- DIOR-R official：100 epochs、batch 32、RAM cache、3 seeds；
- HRSID-derived OBB：100 epochs、batch 8、disk cache、3 seeds；
- 小目标诊断口径：`wh < 1024 px^2`。

### 0.2 已核实但需要注意的外部材料状态

LSKNet 作为第四章首选 Backbone 的依据是成立的：其官方仓库 `https://github.com/zcablii/LSKNet` 明确提供 LSKNet backbone 代码、DOTA1.0 的 `LSKNet_T + ORCNN` 配置和 model 下载入口，也提供 ImageNet 预训练的 LSKNet-T backbone 下载入口。

当前本仓库本地状态为：

- 用户已手动补齐完整 LSKNet 源码到 `research/external_repos/LSKNet/`；
- 用户已手动补齐 DOTA LSKNet-T + Oriented R-CNN checkpoint 到 `weights/pretrained/lsknet/lsk_t_fpn_1x_dota_le90_20230206-3ccee254.pth`；
- 用户已手动补齐 ImageNet LSKNet-T backbone checkpoint 到 `weights/pretrained/lsknet/lsk_t_backbone.pth.tar`，作为备用初始化材料。

本地核验摘要：

- LSKNet-T 官方配置为 `embed_dims=[32, 64, 160, 256]`、`depths=[3, 3, 5, 2]`；
- DOTA checkpoint 可正常读取，`state_dict` 中有 478 个 `backbone.*` key，可提取 backbone 参数量约 3,997,644；
- ImageNet backbone checkpoint 可正常读取，但 key 无 `backbone.` 前缀，适合作为备用权重来源。

### 0.3 已确认的第四章执行决策

1. 第四章新 baseline 严格采用“LSKNet-T Backbone + 必要通道适配层 + 原始 YOLO11 Neck + 原始 YOLO11 OBB Head”，不继承第三章的 FSPB 和 LPCF。换 Backbone 及必要接口适配不作为创新，第四章创新仅为后续 C、D 两个模块。
2. 当前固定使用 LSKNet-T 作为第四章候选 Backbone。LSKNet-S 暂不作为主方案，最多保留为后续骨干选择对比项，避免因扩大模型规模导致精度提升归因不清。
3. 正式实验目标接受两个数据集、四组消融、三随机种子，即 `2×4×3=24` 次完整训练。但采用分阶段流程：先完成 DIOR-R 单种子 baseline 验证，再进行 C、D 单种子筛选，设计成立后才运行两数据集三种子正式实验。
4. 第一阶段只完成纯 LSKNet-T baseline、结构适配和权重转换，不同时设计 C、D。

第一阶段初始化方案暂定为：

- LSKNet-T Backbone 从官方 LSKNet-T + Oriented R-CNN 的 DOTA checkpoint 中提取 backbone 权重；
- YOLO11 Neck 和 OBB Head 尽量从 `yolo11n-obb.pt` 加载兼容权重；
- 新增通道适配层随机初始化。

第一阶段还需输出并记录：

- LSKNet-T 各阶段输出层及通道；
- DOTA Backbone 权重加载成功率；
- YOLO11 Neck/Head 权重加载情况；
- 随机初始化层列表；
- Params、GFLOPs；
- DIOR-R 单种子完整训练结果；
- 与 YOLO11n-OBB 原始 baseline 的对比。

第四章当前不再定位为解决第三章计算量增加的问题，而定位为：第三章从 Neck 和 Head 改善细粒度特征传递与小目标预测；第四章进一步从 Backbone 特征提取阶段增强复杂遥感场景下的自适应感受野和长程上下文建模。第四章核心硬指标为 mAP，参数量与 GFLOPs 如实报告，但暂不要求下降。

## 1. 文档目的

本文档用于约束后续代码实现、实验设计和论文写作。Codex 应以本文件为当前阶段的方案基线，不要自行把第四章改成“继续在原 YOLO11n-OBB 上堆两个模块”，也不要未经确认直接更换成完整的 RTMDet、DETR 或 YOLO26 检测框架。

当前论文主题为遥感旋转目标检测，第三章和第四章应围绕同一任务形成递进关系，但两个创新点需要在研究位置、机制和实验故事上保持明显差异。

---

## 2. 已确定的第三章方案

### 2.1 基础模型

第三章以 `YOLO11n-OBB` 为基线，使用官方 `yolo11n-obb.pt` 初始化。该权重是完整的 DOTA 旋转检测预训练权重，包含：

- YOLO11 原生 Backbone；
- YOLO11 Neck；
- OBB Head。

### 2.2 第三章的创新点

第三章的一个创新点由两个模块共同构成：

- **A：FSPB**，主要引入细尺度特征保持与高分辨率预测路径，是 GFLOPs 大幅增加的主要来源；
- **B：LPCF**，主要进行轻量化的上下文与多尺度特征融合，计算增量相对较小。

A、B 作用位置不同：FSPB 新增 P2/stride-4 预测路径并回流到底向上 PAN，LPCF 只作用于原 top-down P5→P4、P4→P3 两个融合阶段。论文中应以当前实现和已有图示为准，不要擅自调换模块定义。

### 2.3 消融实验形式

第三章已采用标准消融：

| Variant | A | B |
|---|---:|---:|
| Baseline |  |  |
| Baseline + A | ✓ |  |
| Baseline + B |  | ✓ |
| Baseline + A + B | ✓ | ✓ |

主要实验数据集为：

- DIOR-R；
- HRSID。

第四章原则上继续使用相同数据集，不应完全换成另外两个数据集，否则两章最终模型失去直接可比性，也容易被质疑为选择性汇报。

### 2.4 当前第三章关键结果

#### 单次实验结果

| Dataset | Variant | Params (M) | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---|---:|---:|---:|---:|---:|---:|
| DIOR-R | Baseline | 2.658 | 6.6 | 71.11 | 54.31 | 27.32 | 17.96 |
| DIOR-R | Baseline + A + B | 2.740 | 10.7 | 72.25 | 54.55 | 29.20 | 20.42 |
| HRSID | Baseline | 2.654 | 6.6 | 75.13 | 39.63 | 71.60 | 37.36 |
| HRSID | Baseline + A + B | 2.738 | 10.7 | 93.96 | 67.65 | 92.12 | 66.87 |

#### 三随机种子均值结果

| Dataset | Variant | Seeds | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---|---:|---:|---:|---:|---:|
| DIOR-R | Baseline | 3 | 71.02 ± 0.10 | 54.19 ± 0.12 | 27.17 ± 0.16 | 17.79 ± 0.17 |
| DIOR-R | Baseline + A + B | 3 | 72.12 ± 0.14 | 54.43 ± 0.12 | 29.01 ± 0.19 | 20.24 ± 0.18 |
| HRSID | Baseline | 3 | 74.96 ± 0.18 | 39.42 ± 0.21 | 71.37 ± 0.23 | 37.13 ± 0.23 |
| HRSID | Baseline + A + B | 3 | 93.88 ± 0.09 | 67.48 ± 0.17 | 91.99 ± 0.13 | 66.70 ± 0.18 |

### 2.5 对第三章结果的统一解释

第三章最终模型并不是“参数很重”的模型：

- DIOR-R 参数量由 `2.658M` 增至 `2.740M`，约增加 `3.1%`；
- GFLOPs 由 `6.6` 增至 `10.7`，约增加 `62.1%`。

因此第三章的真实特征是：

> 参数规模仍然紧凑，但由于高分辨率细尺度路径，计算量明显上升；其主要收益集中在小目标检测能力，而总体 mAP50:95 的提升相对有限。

DIOR-R 与 HRSID 中同一模型的参数量略有差异是正常现象，原因是两个数据集类别数不同，分类分支输出通道数不同。Backbone 和 Neck 的结构并未因此改变。不要为了表格一致而人为把参数量改成相同值。

---

## 3. 第四章总体方向

### 3.1 不采用的主方案

以下方案不作为当前首选：

1. 继续使用原 YOLO11 Backbone，只在其上再增加 C、D 两个模块；
2. 直接把基础模型整体换成 YOLO26n-OBB；
3. 直接把基础模型整体换成 RTMDet-R 或 DETR；
4. 把第四章强行包装成解决第三章 GFLOPs 增加的轻量化章节。

原因：

- 方案 1 容易导致第三、第四章同质化；
- 方案 2 仍然是 YOLO 版本更替，不能清晰体现“换 Backbone”；
- 方案 3 属于更换完整检测框架，不是严格意义上的只换 Backbone；
- 方案 4 与当前首选 Backbone 的预期复杂度不匹配，实验结果可能反驳论文动机。

### 3.2 当前首选 Backbone

第四章当前优先选择：

> **LSKNet-T Backbone**

理由：

- LSKNet 是针对遥感场景设计的独立 Backbone；
- 具备大范围、选择性空间上下文建模能力；
- 与 YOLO11 原生卷积 Backbone 在理论机制上差异明显；
- 存在基于 DOTA 旋转检测训练的官方完整检测 checkpoint，可从中提取 `backbone.*` 权重；
- 可以构造“只更换 Backbone，保留 YOLO11 Neck 和 OBB Head”的混合模型。

LSKNet-T 只是第四章的基础架构选择，**更换 Backbone 本身不作为本文创新点**。

### 3.3 第四章基础模型结构

第四章的新基线应尽量保持如下结构：

- `LSKNet-T Backbone`；
- 必要的 P3/P4/P5 输出提取；
- 必要的 `1×1 Conv` 或其他最小通道对齐层；
- 原 YOLO11 Neck；
- 原 YOLO11 OBB Head。

即：

    Input
      ↓
    LSKNet-T Backbone
      ↓
    P3 / P4 / P5 feature maps
      ↓
    Minimal channel adapters
      ↓
    YOLO11 Neck
      ↓
    YOLO11 OBB Head

必要的通道适配只属于结构兼容处理，不包装成创新。

---

## 4. 第三章与第四章的论文衔接

第四章不再从“降低第三章计算量”切入，而从第三章仍未充分解决的特征提取问题切入。

### 4.1 第三章解决的问题

第三章主要从特征融合和预测端解决：

- 浅层细粒度信息在逐级下采样中丢失；
- 小目标高分辨率特征传递不足；
- 原始预测分支对旋转小目标的适应能力有限。

第三章的核心关键词：

- 细节保持；
- 高分辨率特征；
- 多尺度融合；
- 小目标预测。

### 4.2 第四章解决的问题

第三章仍然沿用 YOLO11 原生 Backbone，其特征提取主要依赖固定局部卷积。复杂遥感场景中的不同目标在尺寸、形状、方向和上下文范围上差异显著，仅在 Neck 和 Head 端进行补偿，仍可能无法从特征源头充分建模：

- 大范围空间关系；
- 长距离上下文；
- 复杂背景与目标之间的依赖；
- 不同尺度、形状和方向目标所需的自适应感受野。

第四章因此从 Backbone 特征提取阶段切入，引入 LSKNet-T，并在其基础上设计 C、D 两个模块，进一步增强复杂遥感场景中的上下文建模和旋转目标辨识能力。

### 4.3 两章的统一主线

论文整体主线应表述为：

> 第三章从特征融合和预测阶段提升细尺度信息传递与小目标预测能力；第四章进一步从特征提取源头增强自适应感受野和大范围上下文建模能力。

可简化为：

- 第三章回答“细节如何传递与预测”；
- 第四章回答“有效特征如何从源头提取”。

这比“第四章解决第三章的计算量问题”更稳定，也不依赖第四章 Params 或 GFLOPs 必须下降。

---

## 5. 第四章创新点约束

### 5.1 创新点形式

第四章的第二个创新点仍由两个模块组成：

- C；
- D。

更换 LSKNet-T Backbone 不计入创新点。

### 5.2 C、D 不应重复第三章 A、B

应避免：

- 再增加一个与 FSPB 类似的完整高分辨率预测层；
- 再做一个与 LPCF 高度相似的多核 Neck 融合模块；
- 再简单替换一次普通上采样模块；
- 再做一次与第三章同类型的 Head 堆叠。

C、D 更适合围绕 LSKNet-T 和第四章问题设计，例如：

- 旋转目标感知的选择性大核或方向建模；
- 不同尺度目标的自适应感受野调节；
- 浅层细节与深层大范围上下文的跨阶段交互；
- 复杂背景抑制或显著区域增强；
- 旋转框定位、方向信息或标签分配优化；
- 训练阶段辅助监督、蒸馏或特征对齐机制。

最终选型必须以 baseline 实验暴露的问题为依据，不要先随意堆模块，再反向编故事。

---

## 6. 第四章实验目标

### 6.1 核心硬指标

第四章以精度为核心硬指标，优先关注：

- `All mAP50:95`；
- `All mAP50`；
- `Small mAP50:95`；
- `Small mAP50`。

Params、GFLOPs、FPS、Latency、显存仍应报告，但只做复杂度与部署分析，不要求必须低于第三章。

### 6.2 必须满足的章节内部关系

第四章必须证明：

- `LSKNet-T + C` 优于 `LSKNet-T baseline`；
- `LSKNet-T + D` 优于 `LSKNet-T baseline`；
- `LSKNet-T + C + D` 是第四章消融中的最佳或最具综合优势方案。

核心消融表：

| Variant | C | D |
|---|---:|---:|
| LSKNet-T baseline |  |  |
| LSKNet-T + C | ✓ |  |
| LSKNet-T + D |  | ✓ |
| LSKNet-T + C + D | ✓ | ✓ |

### 6.3 跨章节目标

既然第四章定位为进一步提升特征提取与上下文建模能力，最终模型最好在主要精度指标上超过第三章 `A+B`。

当前参考目标：

#### DIOR-R

- 单次结果：第三章 `A+B` 的 All mAP50:95 为 `54.55`，Small mAP50:95 为 `20.42`；
- 三随机种子均值：All mAP50:95 为 `54.43 ± 0.12`，Small mAP50:95 为 `20.24 ± 0.18`。

#### HRSID

- 单次结果：第三章 `A+B` 的 All mAP50:95 为 `67.65`，Small mAP50:95 为 `66.87`；
- 三随机种子均值：All mAP50:95 为 `67.48 ± 0.17`，Small mAP50:95 为 `66.70 ± 0.18`。

上述数值是目标参照，不是允许人为调参或挑种子的理由。正式结果应统一训练协议并报告真实结果。

如果第四章最终模型的参数量和 GFLOPs 增加，则其 mAP 提升必须足够清晰，且最好在复杂背景类别、长宽比大目标、密集目标或小目标专项指标中体现机制优势。

---

## 7. 预训练权重方案

### 7.1 推荐初始化

- LSKNet-T Backbone：从官方 LSKNet-T 旋转检测模型的 DOTA checkpoint 中提取 `backbone.*`；
- YOLO11 Neck 和 OBB Head：从 `yolo11n-obb.pt` 中加载结构兼容的参数；
- 通道适配层、C、D：随机初始化。

### 7.2 必须诚实说明的限制

虽然 LSKNet-T Backbone 与 YOLO11 Neck/Head 分别经过 DOTA 训练，但它们未必在当前混合结构中联合训练过。因此，不能在未做联合预训练时写成：

> “第四章完整模型采用 DOTA 预训练权重。”

更准确的表述是：

> “第四章模型的 LSKNet-T Backbone 采用从 DOTA 旋转检测 checkpoint 中提取的预训练参数，YOLO11 Neck 和 OBB Head 采用官方 YOLO11n-OBB 权重中结构兼容的参数进行初始化。”

### 7.3 最严谨方案

如果算力和时间允许，完成：

    LSKNet-T + YOLO11 Neck + YOLO11 OBB Head
                    ↓
              DOTA 联合训练/微调
                    ↓
             DIOR-R / HRSID 微调

完成该步骤后，才能准确表述为第四章完整混合模型经过 DOTA 旋转检测预训练。

---

## 8. Codex 实现任务

### 8.1 第一阶段：只构建空白新基线

在设计 C、D 前，先完成纯 LSKNet-T Backbone 基线：

1. 在当前 Ultralytics/YOLO11-OBB 代码中注册 LSKNet-T 模块；
2. 新建只替换 Backbone 的 OBB YAML；
3. 保留原 YOLO11 Neck 和 OBB Head；
4. 正确输出 P3、P4、P5；
5. 只添加必要的通道适配层；
6. 确保 `model.info()`、前向传播、训练、验证均可运行；
7. 统计 Params、GFLOPs 和各层输出尺寸；
8. 明确记录 LSKNet-T 各阶段输出层与通道数；
9. 明确记录随机初始化层列表。

### 8.2 第二阶段：DOTA Backbone 权重转换与加载

编写独立转换/加载脚本，要求：

- 读取官方 LSKNet-T DOTA checkpoint；
- 只提取 `backbone.*`；
- 映射为当前实现的键名；
- 对每个键检查形状；
- 输出成功加载、形状不匹配、缺失和多余键；
- 输出加载参数数量和占 Backbone 参数总量的比例；
- 不允许使用 `strict=False` 后静默忽略大量参数；
- 保存转换后的纯 Backbone 权重，便于复现实验。
- 第一阶段报告中必须给出 DOTA Backbone 权重加载成功率。

### 8.3 第三阶段：YOLO11 Neck/Head 权重加载

- 从 `yolo11n-obb.pt` 提取结构兼容的 Neck 和 OBB Head 参数；
- 对通道变化导致的不兼容层明确记录；
- 输出 transferred items 统计；
- 不允许把未加载成功描述为“已使用完整 YOLO11 预训练权重”。
- 第一阶段报告中必须列出 Neck/Head 已加载层、未加载层与随机初始化层。

### 8.4 第四阶段：预筛实验

先在 DIOR-R 上运行 LSKNet-T 空白基线：

- 使用与第三章相同的数据划分；
- 使用相同输入尺寸；
- 使用相同评价脚本；
- 使用相同小目标定义；
- 保存训练日志、最佳权重和最终权重；
- 记录 Params、GFLOPs、FPS、Latency、显存、All/Small mAP。
- 与第三章 YOLO11n-OBB 原始 baseline 作同协议对比，先判断 Backbone 替换是否具备继续设计 C、D 的基础。

短周期实验只能用于结构与趋势预筛，不可作为论文最终结果。候选进入正式实验后必须完整训练。

### 8.5 第五阶段：根据 baseline 问题设计 C、D

在获得 LSKNet-T baseline 结果后，再决定 C、D：

- 若复杂背景误检明显，优先设计背景抑制或上下文选择模块；
- 若小目标下降明显，优先设计低成本细节补偿或跨阶段交互；
- 若旋转框定位差，优先设计方向/角度相关优化；
- 若总体分类能力好但定位不足，优先改定位损失、标签分配或方向监督。

不要在 baseline 结果未知时一次性加入多个不相关模块。

---

## 9. 正式实验规范

第三、第四章及所有对比实验尽量统一：

- 数据集划分；
- 输入尺寸；
- batch size 或等效梯度累积；
- 数据增强策略；
- 训练轮数和 early stopping 规则；
- 优化器和学习率策略，若因 Backbone 特性必须调整，应明确说明；
- 随机种子；
- 小目标定义；
- 评价脚本；
- 推理硬件；
- FP32/FP16 模式；
- 单尺度测试或多尺度测试设置。

最终至少报告：

- 单次最佳结果；
- 三随机种子均值与标准差；
- Params；
- GFLOPs；
- FPS；
- Latency；
- GPU 显存；
- All mAP50；
- All mAP50:95；
- Small mAP50；
- Small mAP50:95。

不同模型使用的预训练来源必须单独列出，不能笼统写“所有模型均采用相同预训练权重”。

---

## 10. 推荐的论文表格

### 10.1 Backbone 基线选择表

| Model | Backbone | Pretraining | Params | GFLOPs | All mAP50:95 | Small mAP50:95 |
|---|---|---|---:|---:|---:|---:|
| YOLO11n-OBB | YOLO11 native | DOTA full detector |  |  |  |  |
| Chapter 3 A+B | YOLO11 native | DOTA full detector |  |  |  |  |
| New baseline | LSKNet-T | DOTA backbone + compatible YOLO weights |  |  |  |  |

### 10.2 第四章核心消融表

| Variant | C | D | Params | GFLOPs | All mAP50 | All mAP50:95 | Small mAP50 | Small mAP50:95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LSKNet-T baseline |  |  |  |  |  |  |  |  |
| LSKNet-T + C | ✓ |  |  |  |  |  |  |  |
| LSKNet-T + D |  | ✓ |  |  |  |  |  |  |
| LSKNet-T + C + D | ✓ | ✓ |  |  |  |  |  |  |

### 10.3 跨章节综合比较表

| Model | Backbone | All mAP50:95 | Small mAP50:95 | Params | GFLOPs | FPS | Latency |
|---|---|---:|---:|---:|---:|---:|---:|
| YOLO11n-OBB baseline | YOLO11 native |  |  |  |  |  |  |
| Chapter 3 A+B | YOLO11 native |  |  |  |  |  |  |
| Chapter 4 baseline | LSKNet-T |  |  |  |  |  |  |
| Chapter 4 C+D | LSKNet-T |  |  |  |  |  |  |

---

## 11. 推荐的章节标题与衔接表述

### 11.1 第三章标题方向

> 基于细尺度保持与上下文融合的遥感旋转小目标检测方法

或：

> 面向遥感旋转小目标的多尺度特征融合与预测增强方法

### 11.2 第四章标题方向

> 基于选择性大核上下文建模的遥感旋转目标检测方法

或：

> 面向复杂遥感场景的自适应感受野旋转目标检测方法

### 11.3 第三章结尾衔接参考

> 本章通过细尺度特征保持分支和上下文融合模块，增强了网络对遥感旋转小目标的特征传递与预测能力。然而，该方法仍沿用YOLO11原始卷积骨干，其特征提取主要依赖固定局部感受野。复杂遥感场景中不同目标在空间尺度、几何形态、方向和所需上下文范围方面存在显著差异，仅依靠Neck和检测头的改进仍难以从特征源头充分建模大范围空间关系与长距离上下文信息。因此，下一章将进一步从骨干特征提取阶段研究具有自适应感受野的旋转目标检测方法。

### 11.4 第四章开头参考

> 针对原始卷积骨干在复杂遥感场景中对大范围上下文和差异化感受野建模不足的问题，本章引入面向遥感图像设计的LSKNet-T骨干网络，并在此基础上提出C模块和D模块，以增强网络对不同尺度、不同形态及不同方向旋转目标的自适应上下文建模能力，进一步提高旋转目标检测精度。

---

## 12. 风险与回退方案

### 12.1 主要风险

- LSKNet-T Backbone 与当前 Ultralytics 实现的结构或参数名无法完全对应；
- DOTA checkpoint 来自其他检测框架，Backbone 虽可迁移，但与 YOLO11 Neck/Head 未联合训练；
- LSKNet-T baseline 的 Params/GFLOPs 可能明显增加；
- LSKNet-T baseline 在 DIOR-R/HRSID 上未必直接优于 YOLO11n-OBB；
- C、D 若继续集中在 Neck/Head，可能与第三章同质化；
- 第四章复杂度增加但 mAP 未超过第三章，论文说服力会下降。

### 12.2 回退优先级

1. 先尝试对混合模型进行 DOTA 联合预训练或短期微调；
2. 调整 LSKNet-T 输出阶段与 YOLO11 Neck 的通道适配；
3. 根据失败类型设计 C、D，而不是继续堆通用注意力；
4. 若 LSKNet-T 不可行，再评估 PKINet-T 或 CSPNeXt 等有 DOTA 旋转检测 checkpoint 的 Backbone；
5. YOLO26n-OBB 可作为工程保底方案，但不是当前论文首选；
6. 直接换 RTMDet/DETR 属于换完整基础模型，应视为另一套论文结构，未经确认不要执行。

---

## 13. 当前最终共识

1. 第三章维持 `YOLO11n-OBB + FSPB(A) + LPCF(B)`；
2. 第三章的主要贡献是提升小目标特征保持和预测能力，参数增加很少，但 GFLOPs 增加明显；
3. 第四章不再围绕“解决第三章计算量问题”展开；
4. 第四章严格采用“换 Backbone，不换完整检测框架”的思路；
5. 当前首选 Backbone 为 `LSKNet-T`；
6. 第四章尽量保留 YOLO11 Neck 和 OBB Head，仅做必要通道适配；
7. LSKNet-T 的引入不是创新，C、D 才构成第二个创新点；
8. 第四章主线是增强自适应感受野、大范围空间关系和复杂遥感上下文建模；
9. 第四章硬指标以 mAP 为主，Params 和 GFLOPs 可以增加，但必须如实报告；
10. 第四章最终 `LSKNet-T + C + D` 必须明显优于自己的新 Backbone baseline，并最好超过第三章 `A+B` 的主要 mAP 指标；
11. 第三、第四章继续使用 DIOR-R 和 HRSID，保持统一实验协议和可比性；
12. Codex 当前第一任务不是直接设计 C、D，而是先完成纯 `LSKNet-T + YOLO11 Neck + YOLO11 OBB Head` 基线、权重映射、参数加载核验和初步训练。
