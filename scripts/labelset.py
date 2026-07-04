import os

remap = {0: 0, 10: 1, 11: 2}
keep = set(remap.keys())

for split in ["train", "val"]:
    src_dir = f"C:/E/download/DOTAv1_split/labels/{split}"
    dst_dir = f"C:/E/download/DOTAv1_split/labels_remapped/{split}"  # 新目录
    os.makedirs(dst_dir, exist_ok=True)

    for fname in os.listdir(src_dir):
        if not fname.endswith(".txt"):
            continue
        src_path = os.path.join(src_dir, fname)
        dst_path = os.path.join(dst_dir, fname)  # 写到新目录
        new_lines = []
        with open(src_path) as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                cls = int(parts[0])
                if cls in keep:
                    parts[0] = str(remap[cls])
                    new_lines.append(" ".join(parts))
        with open(dst_path, "w") as f:
            f.write("\n".join(new_lines))

print("重映射完成，原始文件未改动")
