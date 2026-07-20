# IPPR 2026 小论文写作说明

> 状态：写作前准备完成，尚未开始论文正文。  
> 最后核对日期：2026-07-20。  
> 用途：供后续 Codex、Claude Code 或人工写作时首先阅读，统一论文主线、证据、术语、实验边界和 LaTeX 交付要求。

## 1. 投稿目标与硬约束

- 目标会议：2026 3rd International Conference on Intelligent Perception and Pattern Recognition（IPPR 2026）。
- 会议主页：<https://www.icippr.org/>。
- 艾思科蓝页面：<https://www.ais.cn/attendees/index/JBQYMB>。
- 截稿时间：2026-07-31 23:59；会议时间：2026-08-14 至 2026-08-16，中国重庆。
- 出版与检索：会议方称录用论文由 IEEE 会议论文集出版，并提交 IEEE Xplore、EI Compendex 和 Scopus。
- 投稿形式：英文全文、IEEE 双栏，至少 4 页。艾思科蓝页面列出的基础注册为 4 页，第 5 页起收取超页费。
- 主题匹配：目标检测、计算机视觉、遥感图像解译、深度学习和轻量化模型均在征稿范围内。
- 原创性：论文不得已发表或同时投往其他会议/期刊；会议页面要求作者自行保证内容准确、原创和无学术不端。
- 模板来源：`C:/E/培养方案/小论文/Templates/Conference-LaTeX-template_10-17-19/`。
- 主模板：`conference_101719.tex`，文档类为 `IEEEtran` 的 `conference` 模式。
- 投稿系统要求同时上传两项：PDF 格式论文（必传），以及 Word 或 LaTeX ZIP 格式源文件（二选一，必传）。本项目采用 LaTeX 路线，因此最终交付物为编译后的 PDF 和 LaTeX 源码 ZIP，无需另行准备 Word 文档。

会议官方 AI 工具规则：<https://www.icippr.org/GuidelinesforAITools>。会议允许使用生成式 AI 辅助语言和格式编辑，但作者必须逐项核验内容、引用、数据和图表，并在 Methodology 或 Acknowledgment 中披露工具名称、版本、功能和具体用途。AI 不得列为作者，也不得生成或篡改实验数据。

## 2. 当前写作判断

论文已经具备成文所需的核心实验链：

1. DIOR-R 上 baseline、A-P2、B-PKI-Lite 和 A+B-PKI-Lite 完整，AB 为最优。
2. HRSID 上四组协议一致，四项均满足 `AB > A > B > baseline`。
3. A 与 B 位于不同结构位置，具备清晰消融边界。
4. 参数量和 GFLOPs 已有统一口径，AB 相对 DIOR-R baseline 仅增加约 3.11% 参数。

但“可以开始写”不等于“已经可以直接投稿”。正式定稿前仍需完成：近期方法对比、定性可视化、作者与单位信息、参考文献核验、页数决定、AI 使用披露和最终 LaTeX 编译检查。

## 3. 论文定位

### 3.1 论文类型

- 类型：algorithmic conference paper。
- 主要读者：遥感目标检测、旋转框检测、微小目标检测和轻量化视觉模型研究者。
- 核心问题：YOLO11n-OBB 的默认 P3/P4/P5 检测尺度是否会损失遥感微小旋转目标信息，以及多尺度上下文是否能进一步改善融合特征。

### 3.2 一句话论点

在遥感小目标旋转框检测中，在 YOLO11n-OBB 中增加 P2/4 检测分支，并在原 top-down neck 融合块中加入轻量多核上下文建模，可在有限参数增量下改善 DIOR-R 和 HRSID 上的全尺度及小目标检测性能；该结论的边界是 B 的独立增益较小。

### 3.3 暂定贡献结构

1. **A-P2：细粒度检测尺度增强。** 在检测 head 中引入 P2/4 输出，使 OBB head 使用 P2/P3/P4/P5 四尺度特征，强化微小目标的空间细节。
2. **B-PKI-Lite：轻量多核上下文融合。** 在 top-down neck 的 P5->P4、P4->P3 两个原融合块中使用 `C3k2PKI`，通过多核 depthwise 分支与上下文门控改善尺度和背景建模。
3. **互补融合与跨数据集验证。** A 负责检测尺度，B 负责 neck 融合；组合模型在 DIOR-R 和 HRSID 的固定消融协议下进一步提升 A，并保持较小参数增量。

以上贡献不能扩写成“三个创新点”。EI 小论文只写 A、B 和 AB；C 系列留给学位论文或后续工作。

## 4. 术语账本

| 规范术语 | 首次出现建议 | 禁止或需避免的变体 |
|---|---|---|
| YOLO11n-OBB | YOLO11n oriented bounding-box detector（YOLO11n-OBB） | YOLOv11n-OBB，除非引用来源使用该写法 |
| oriented bounding box | oriented bounding box（OBB） | rotated box、rotating box 混用 |
| A-P2 | P2 detection-branch enhancement（A-P2） | P2-Plus、A-Plus；它们不是论文主方法 |
| B-PKI-Lite | lightweight poly-kernel context fusion（B-PKI-Lite） | B-LSK、PKI-Heavy；均不是论文主方法 |
| A+B-PKI-Lite | combined A-P2 and B-PKI-Lite model | ABC、AB-Plus、Heavy、Decoupled |
| C3k2PKI | 本仓库 B 模块实现名 | 不声称它等同完整 PKINet |
| DIOR-R | DIOR-R remote-sensing OBB dataset | DIOR 与 DIOR-R 混用 |
| HRSID-derived OBB | OBB labels derived from HRSID instance masks | 不写成“官方原生 HRSID OBB 标注” |
| small object | letterbox 后 OBB 面积小于 1024 像素的目标 | 不直接称为 COCO small，除非明确说明协议不同 |
| mAP50 | mean average precision at IoU 0.50 | AP50/mAP@0.5 可在表头统一，但正文不要漂移 |
| mAP50-95 | mean AP averaged from IoU 0.50 to 0.95 | mAP、COCO mAP 未定义时不要单独使用 |

总体方法名尚未锁定。可暂用内部占位名 `P2-PKI-YOLO`，正式标题与正文首次出现前必须由作者确认，不能由写作代理自行定名。

## 5. 可用于正文的核心证据

Seed 仅在 Experimental Settings 中作为复现超参数简要说明。`42` 是深度学习实验中常见的约定性取值，`3407` 则因计算机视觉领域关于随机种子影响的公开研究而具有较高辨识度；二者的作用都是固定随机过程，不代表某个数值具有理论上的精度优势。论文可统一表述为：为保证组内比较公平和结果可复现，DIOR-R 与 HRSID 分别固定使用 `seed=42` 和 `seed=3407`，且同一数据集内 baseline、A、B 和 AB 使用完全相同的 seed 与确定性设置。正文不展开 seed 筛选过程，也不声称特定 seed 能带来更好的收敛或精度。

### 5.1 DIOR-R：主数据集

训练协议：`epochs=100`、`batch=4`、`imgsz=640`、`seed=42`、`deterministic=True`、`cache=disk`，四组均从 `weights/pretrained/yolo11n-obb.pt` 独立起训。

数据划分为本项目所用第三方 YOLODIOR-R 的 18,770 train / 2,346 val / 2,347 test，而不是 DIOR-R 论文常用的 5,862 train / 5,863 val / 11,738 test 官方划分。正文必须披露该差异；当前结果只用于同一划分下的内部消融，不能与官方划分上的公开 AP50 直接排名。

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 2,657,623 | 6.6 | 0.8588 | 0.6874 | 0.5146 | 0.3470 |
| A-P2 | 2,698,340 | 10.5 | 0.8779 | 0.6990 | 0.5830 | 0.4215 |
| B-PKI-Lite | 2,699,673 | 6.8 | 0.8588 | 0.6885 | 0.5249 | 0.3621 |
| A+B-PKI-Lite | **2,740,390** | **10.7** | **0.8859** | **0.7198** | **0.5958** | **0.4288** |

AB 相对 baseline：参数量 `+82,767`（`+3.11%`），全尺度 mAP50/mAP50-95 `+0.0271/+0.0324`，小目标 mAP50/mAP50-95 `+0.0812/+0.0818`。

### 5.2 HRSID-derived OBB：第二数据集

训练协议：`epochs=100`、`batch=8`、`imgsz=640`、`seed=3407`、`deterministic=True`、`cache=disk`，四组均从相同官方预训练权重独立起训。

| 模型 | Params | GFLOPs | 全尺度 mAP50 | 全尺度 mAP50-95 | 小目标 mAP50 | 小目标 mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 2,653,918 | 6.6 | 0.7513 | 0.3963 | 0.7160 | 0.3736 |
| A-P2 | 2,695,832 | 10.5 | 0.9371 | 0.6706 | 0.9178 | 0.6610 |
| B-PKI-Lite | 2,695,968 | 6.8 | 0.7620 | 0.4191 | 0.7273 | 0.3888 |
| A+B-PKI-Lite | **2,737,882** | **10.7** | **0.9396** | **0.6765** | **0.9212** | **0.6687** |

B 相对 baseline 四项为 `+0.0107/+0.0228/+0.0113/+0.0152`；AB 相对 A 为 `+0.0025/+0.0059/+0.0034/+0.0077`；AB 相对 baseline 为 `+0.1883/+0.2802/+0.2052/+0.2951`。

### 5.3 HRSID 数据协议必须披露

- 使用官方 HRSID JPG 与 COCO instance segmentation 标注。
- 通过 OpenCV `minAreaRect` 从实例轮廓生成最小面积四点 OBB，而不是使用官方原生 OBB。
- 保留官方 1962 张 test；从官方 3642 张 train 按 inshore/offshore 分层固定抽取 10% 为 val。
- 最终 train/val/test 为 3278/364/1962 张图和 9974/1064/5918 个 OBB。
- 13 个面积不超过 1 像素的退化轮廓被丢弃。
- test 中有 5350 个目标符合本项目小目标协议。

### 5.4 小目标协议必须披露

本仓库的小目标评估不是 COCO 官方 area 分档。图像 letterbox 到 `imgsz=640` 后，以 OBB 宽高面积 `w*h<1024` 选择小目标，并同步过滤 GT 与预测。正文、表注和图注必须写清阈值、计算空间和筛选对象，不能只写 “small-object AP”。

## 6. 主张-证据映射

| 主张 | 直接证据 | 状态与边界 |
|---|---|---|
| A-P2 改善微小旋转目标检测 | DIOR-R 与 HRSID 的 A 对 baseline 四项差值 | 支持；HRSID 增益远大于 DIOR-R，需避免泛化为所有数据集 |
| B-PKI-Lite 提供轻量上下文增益 | 两数据集 B 的 mAP50-95 与小目标指标 | 支持但幅度小；DIOR-R 全尺度 mAP50 持平 |
| A 与 B 在 DIOR-R 上互补 | AB 的四项主要精度指标均超过 A/B/baseline | 强支持 |
| A 与 B 在 HRSID 上互补 | AB 的四项主要精度指标均超过 A/B/baseline | 支持 |
| 方法保持轻量 | DIOR-R AB 参数仅增加 3.11%，GFLOPs 6.6->10.7 | 参数支持；计算量增幅明显，不能只写“negligible overhead” |
| 方法适用于两类遥感场景 | DIOR-R 光学多类别 + HRSID SAR 单类舰船 | 有限支持；只有两个数据集，不能声称广泛通用 |

## 7. 不得写入正文的内容

- 不把 C-Dynamic、C-Plus、C-GRA、C-Chol、C-SET-HBS 作为本篇贡献。
- 不把 B-PKI-Lite 说成完整复现 PKINet；应写为 PKINet-inspired lightweight context block，并准确引用来源。
- 不把 HRSID-derived OBB 说成官方原生旋转框数据集。
- 不跨数据集或跨训练协议拼接同一张消融表。
- 不使用 UCAS-AOD、VEDAI、SSDD-RBox、HRSC2016 的负向筛选结果来暗示主方法增益。
- 不写 `state-of-the-art`、`first`、`significant`、`robust`、`universal`，除非后续证据和统计检验确实支持。
- 不把参数增幅小等同于计算开销小；P2 分支使 GFLOPs 从 6.6 增加到 10.7。
- 不生成不存在的引用、实验、显著性检验、FPS、硬件延迟、误差条或可视化案例。

## 8. 建议论文结构与页数预算

模板至少 4 页。建议优先准备 5 页版本，再根据作者是否接受超页费压缩到 4 页或保留 5 页。参考文献是否计入页数须在投稿前向会议秘书确认。

1. **Title / Abstract / Keywords：约 0.35 页。** 标题具体可检索；摘要包含问题、A/B 方法、两个数据集和最强定量结果。
2. **I. Introduction：约 0.65 页。** 遥感 OBB 小目标问题、YOLO11n-OBB 尺度/上下文缺口、贡献列表。
3. **II. Related Work：约 0.45 页。** 遥感 OBB、微小目标多尺度检测、PKI/大核上下文，按主题组织而非逐篇罗列。
4. **III. Method：约 1.0 页。** 总体框架、A-P2、B-PKI-Lite、复杂度；配一张双栏方法总图。
5. **IV. Experiments：约 1.6 页。** 数据与协议、与现有方法比较、消融、复杂度、定性结果。
6. **V. Conclusion：约 0.2 页。** 贡献、决定性证据、边界。
7. **References：约 0.7 至 1.0 页。** 按最终引用数量调整。

## 9. 必需图表

### 必需

1. **Fig. 1 方法总图：** baseline、A-P2 新增路径、B-PKI-Lite 两个替换位置，颜色和图例统一。
2. **Table I 数据集与协议：** 数据集、类别、train/val/test、OBB 数量、小目标数量和主要训练参数。
3. **Table II 与近期方法比较：** 优先使用 HRSID 上与本项目标签生成和官方 test 接近的公开结果；DIOR-R 公开结果因划分不同须独立说明，不与本项目数值直接排名。检索记录见 `paper/RECENT_METHOD_COMPARISON_RESEARCH.md`。
4. **Table III 核心消融：** baseline、A、B、AB，分数据集展示 mAP50 与 mAP50-95；小目标指标可放同表或紧凑子表。
5. **Table IV 复杂度：** Params、GFLOPs，若补测再加入 FPS/latency。
6. **Fig. 2 定性对比：** baseline 与 AB 在密集微小目标、复杂背景、旋转目标上的预测，使用真实模型输出。

### 可选

- 目标尺度分布图，用于解释 HRSID 对 P2 分支的高敏感性。
- 失败案例图，体现远小目标、近岸杂波、密集遮挡等边界。

图表一律从真实日志、标签和预测生成。不得使用生成式 AI 绘制或修改实验结果图；方法示意图可以由代码/矢量工具绘制，但必须由作者核对结构真实性。

## 10. 投稿前仍缺少的证据

1. **近期方法对比定稿。** 已完成第一轮检索并找到 HRSID 的 YOSDet、TIAR-SAR、CLAFANet 等可引用结果，以及 DIOR-R 的 PKINet、OrientedFormer、ReDiffDet 和 OpenRSD 报告值。详细数值与协议审计见 `paper/RECENT_METHOD_COMPARISON_RESEARCH.md`；写入正文前仍需完成 BibTeX 核验和最终表格取舍。
2. **定性预测。** 从 DIOR-R 和 HRSID 各选 2 至 4 张，统一置信度和可视化样式。
3. **推理效率。** Params/GFLOPs 已有；FPS/latency 尚未统一测量。若写实时或高效，必须在同一硬件、batch 和预热条件下补测。
4. **作者信息。** 姓名、顺序、单位、城市、国家、邮箱/ORCID、通讯作者。
5. **资助信息。** 无资助则删除模板中的 `\thanks{}`，不能保留占位符。
6. **页数决定。** 4 页基础版还是支付超页费的 5 页版。
7. **方法总名。** `P2-PKI-YOLO` 只是占位名，需作者确认。

## 11. 参考文献计划

引用必须优先读原论文和官方资料，并逐条核验 DOI、作者、年份和页码。最低覆盖：

- YOLO/Ultralytics 与 YOLO11n-OBB 基础来源；若 YOLO11 无正式论文，应准确引用官方软件或文档，不伪造论文。
- DIOR-R 数据集原论文。
- HRSID 数据集原论文。
- DOTA 或遥感 OBB 任务的代表性来源。
- 微小目标多尺度/P2 检测分支相关工作。
- PKINet / Poly Kernel Inception Network，CVPR 2024 原论文。
- 2024 年及以后遥感旋转检测、轻量多尺度融合的相关工作。

正式检索时使用 nature-academic-search 或可信学术数据库；技术事实优先引用论文原文、出版社页面和官方代码。不得引用搜索摘要作为证据。

## 12. LaTeX 工作约定

正式开始时，不直接覆盖原模板。建议复制为：

```text
paper/ippr2026/
  main.tex
  references.bib
  IEEEtran.cls
  figures/
  tables/
  build/
```

当前环境验证：TeX Live 2026 的 `pdflatex` 已于 2026-07-20 成功编译原始模板，输出 3 页 PDF。当前 `latexmk` 的 TeX Live Lua 包装器会报 `attempt to concatenate a nil value`，因此在修复前使用下面的直接编译流程：

```bash
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

若暂时使用模板内置的 `thebibliography` 而非 `.bib`，运行两次 `pdflatex` 即可。修复 `latexmk` 后可恢复：

```bash
latexmk -pdf -bibtex -interaction=nonstopmode -halt-on-error main.tex
```

不得修改 IEEEtran 的页边距、字号、栏宽和行距来强行塞页。表格优先使用 `booktabs`，表题在上、图题在下，`\label` 放在 `\caption` 后。所有引用、图表编号和公式必须通过交叉引用生成。

LaTeX ZIP 应包含可独立编译论文所需的全部源文件：`main.tex`、`IEEEtran.cls`、`references.bib`（若使用 BibTeX）、正文实际引用的图片，以及依赖的非标准 `.sty`、表格或其他输入文件。打包前应在一个干净的临时目录中重新编译，确认不存在本机绝对路径或缺失依赖。

源码 ZIP 不包含训练权重、数据集、`runs/`、缓存、未使用图片和编译中间文件，如 `.aux`、`.log`、`.fls`、`.fdb_latexmk`、`.synctex.gz`。PDF 在投稿系统中单独上传，除非系统另有提示，否则无需重复放入 LaTeX ZIP。

## 13. 后续写作流程

1. 作者确认方法总名、标题方向、作者信息和页数预算。
2. 建立术语账本和一页中文论证提纲，先确认论点，不直接写满英文。
3. 检索并核验相关工作，建立 `references.bib` 与引用证据表。
4. 先制作主消融表、方法总图和定性图，再从证据向外写正文。
5. 写作顺序：Experiments -> Method -> Introduction/Related Work -> Conclusion -> Abstract -> Title。
6. 每个性能主张同时标明数据集、指标、baseline 和训练条件。
7. 使用 nature-writing 起草，nature-polishing 做英文收敛；作者逐句确认技术含义。
8. 编译 PDF，检查双栏溢出、孤行、图表清晰度、字体嵌入、引用与页数。
9. 做引用真实性审计、数值回查、查重和 AI 辅助使用披露。
10. 同时上传编译后的 PDF（必传）和 LaTeX 源码 ZIP（Word/LaTeX ZIP 二选一中的 LaTeX 路线，必传），不把训练权重、数据集或无关构建文件打包。

## 14. AI 使用披露占位

最终措辞必须结合实际使用版本由作者确认。可在 Acknowledgment 中放置类似结构，但不要现在直接粘进论文：

```text
Generative AI tools were used only to assist with language editing, manuscript organization, and LaTeX formatting. All technical claims, experimental results, figures, and references were verified by the authors, who take full responsibility for the content.
```

正式版还需按 IPPR 规则补充工具名称、版本和具体用途。若后续 AI 参与了文献分类、图表代码或数据分析，也必须如实列出；不得笼统写成只做语法修改。

## 15. 权威数据入口

- DIOR-R 总表与主结果：`README.md`、`AGENTS.md`。
- DIOR-R AB：`weights/experiments/dior/ab_p2_pki_lite/eval_dior_test_2026-07-13.md`。
- HRSID 最终消融：`weights/experiments/hrsid/eval_hrsid_test_2026-07-19.md`。
- HRSID 数据与命令：`experiments/hrsid/README.md`。
- HRSID 转换脚本：`scripts/convert_hrsid_to_yolo_obb.py`。
- 第二数据集筛选边界：`research/datasets/SECOND_DATASET_SELECTION.md`。
- 模型 YAML：`ultralytics/cfg/models/11/remote_obb/`。
- A/B 模块代码：`ultralytics/nn/modules/remote_obb_blocks.py`。

后续写作代理必须先读取本文件，再读取对应证据文件。若本文档与训练日志或评估脚本输出冲突，以可复现的原始输出为准，并先修正文档后继续写作。
