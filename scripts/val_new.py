import os
from ultralytics import YOLO

# Load the model
model = YOLO('C:\\E\\github\\ultralytics\\runs\\obb\\train10\\weights\\best.pt')
model = model.to('cuda:0')

print("\n" + "="*50)
print("🚀 第一轮：评估 DIOR-R 数据集上的【所有尺度目标】")
print("="*50)
# 关闭小目标过滤，执行正常的全局评估
os.environ['EVAL_SMALL_ONLY'] = '0'  
metrics_all = model.val(data="DIOR.yaml", split='test', device='0', workers=0)

print("\n" + "="*50)
print("🔬 第二轮：专门评估 DIOR-R 上的【小目标 (Area < 1024)】")
print("="*50)
# 开启小目标过滤，YOLO 会在底层自动忽略所有中大目标
os.environ['EVAL_SMALL_ONLY'] = '1'  
metrics_small = model.val(data="DIOR.yaml", split='test', device='0', workers=0)

# ==========================================
# 📊 提取并打印最终的对比表格数据
# ==========================================
print("\n🎉 评估完成！可以直接填入论文表格的数据如下：")
print("-" * 50)
print(f"🌟 【全局】所有目标 mAP@50:    {metrics_all.box.map50:.4f}")
print(f"🌟 【全局】所有目标 mAP@50-95: {metrics_all.box.map:.4f}")
print("-" * 50)
print(f"🎯 【小目标】(<32x32) mAP@50:    {metrics_small.box.map50:.4f}")
print(f"🎯 【小目标】(<32x32) mAP@50-95: {metrics_small.box.map:.4f}")
print("-" * 50)

# 如果你需要查看每个类别的指标，可以像下面这样调用：
# print("所有类别的全局 mAP50-95:", metrics_all.box.maps)
# print("所有类别的小目标 mAP50-95:", metrics_small.box.maps)