1. 太陽くん作成データをall配下に全てまとめる（1907枚の画像）
1. multi_annot_files配下のtxtをall配下にcopy
1. python make_crops.py && python yolo2pascal/yolo2voc.py ./cropped
1. testを分ける（2020-06-15-で始まるjpgだけ移動させればok）
