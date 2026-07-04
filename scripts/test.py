# 导入torch库
import torch

# 1. 检查CUDA是否可用（核心验证）
print("CUDA是否可用:", torch.cuda.is_available())

# 2. 查看可用的GPU数量
print("可用GPU数量:", torch.cuda.device_count())

# 3. 查看当前使用的GPU索引（如果有GPU）
if torch.cuda.is_available():
    print("当前GPU索引:", torch.cuda.current_device())
    # 4. 查看GPU名称
    print("GPU名称:", torch.cuda.get_device_name(0))

    # 5. 简单的张量运算验证（将张量放到GPU上计算）
    # 创建一个张量并移到GPU
    x = torch.tensor([1.0, 2.0, 3.0]).cuda()
    print("\nGPU上的张量:", x)
    print("张量所在设备:", x.device)
