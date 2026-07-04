# InternImage / DCNv3

## 基本信息

- 论文：InternImage: Exploring Large-Scale Vision Foundation Models with Deformable Convolutions
- 会议：CVPR 2023
- 论文链接：https://openaccess.thecvf.com/content/CVPR2023/html/Wang_InternImage_Exploring_Large-Scale_Vision_Foundation_Models_With_Deformable_Convolutions_CVPR_2023_paper.html
- PDF：https://openaccess.thecvf.com/content/CVPR2023/papers/Wang_InternImage_Exploring_Large-Scale_Vision_Foundation_Models_With_Deformable_Convolutions_CVPR_2023_paper.pdf
- 官方代码：https://github.com/OpenGVLab/InternImage

## 可借鉴点

DCNv3 通过动态采样增强空间适应能力。遥感 OBB 目标具有方向任意、长宽比变化大、密集排列等特点，因此动态采样可以作为“旋转目标几何适应”的动机来源。

## 迁移到 YOLO11n-OBB 的方案

优先级从高到低：

1. 不整体替换 backbone，只在 neck 或检测头前加入一个轻量 deformable block。
2. 如果依赖复杂，改用已有 PyTorch/torchvision 可用的 deformable conv 实现。
3. 如果 DCNv3 编译成本太高，则把它降级为备选，不影响 A+B 主线。

## 风险

- DCNv3 可能依赖自定义 CUDA，Windows 环境编译成本较高。
- 参数和速度开销可能不适合 YOLO11n。
- 如果实现不稳定，不建议作为第一优先级创新点。

