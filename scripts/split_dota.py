from ultralytics.data.split_dota import split_trainval

if __name__ == "__main__":
    # split_trainval(
    #     data_root="C:/E/download/DOTAv1",
    #     save_dir="C:/E/download/DOTAv1_split",
    #     rates=[0.5, 1.0, 1.5],
    #     gap=500,
    # )

    # split_test(
    #     data_root="C:/E/download/DOTAv1",
    #     save_dir="C:/E/download/DOTAv1_split",
    #     rates=[0.5, 1.0, 1.5],
    #     gap=500,
    # )

    split_trainval(
        data_root="C:/E/download/DOTAv1",
        save_dir="C:/E/download/DOTAv1_split",
        rates=[1.0, 1.5],  # 去掉0.5，专注中大尺度，对小目标更友好
        gap=200,  # gap从500改小，减少切片间重叠浪费
    )
