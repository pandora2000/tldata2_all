import os, shutil, cv2, numpy as np
def write_cropped_im(dpath, fname, size, crop_size, crop_index, crop_loc, cropped_im, ngemptyi, ignore_empty):
    fnamewox = fname[:-4]
    cropped_fname = f'{fnamewox}_{crop_index[0]}_{crop_index[1]}.jpg'
    tfpath = f'{dpath}/all/{fnamewox}.txt'
    tdata = None
    with open(tfpath) as f:
        tdata = [[int(y) if i == 0 else float(y) for i, y in enumerate(x.split(' '))] for x in f.read().strip().split('\n')]
    cropped_tdata = []
    gray = False
    for td in tdata:
        loc = [int(round(size[i] * (td[2 - i] - td[4 - i] / 2))) for i in range(2)]
        loc_size = [int(round(size[i] * td[4 - i])) for i in range(2)]
        loc_max = [loc[i] + loc_size[i] for i in range(2)]
        cropped_loc = [max([0, loc[i] - crop_loc[i]]) for i in range(2)]
        cropped_max = [min([loc_max[i] - crop_loc[i], crop_size[i]]) for i in range(2)]
        # print(f'loc: {loc}')
        # print(f'loc_size: {loc_size}')
        # print(f'loc_max: {loc_max}')
        # print(f'crop_index: {crop_index}')
        # print(f'crop_loc: {crop_loc}')
        # print(f'cropped_loc: {cropped_loc}')
        # print(f'cropped_max: {cropped_max}')
        if any([cropped_loc[i] >= cropped_max[i] for i in range(2)]):
            continue
        if any([cropped_max[i] - cropped_loc[i] != loc_size[i] for i in range(2)]):
            print(f'gray zone rendered on {crop_index}')
            cropped_im[cropped_loc[0]:cropped_max[0], cropped_loc[1]:cropped_max[1]] = 127
            gray = True
            continue
        cropped_center_p = [(cropped_loc[i] + cropped_max[i]) / 2 / crop_size[i] for i in range(2)]
        loc_size_p = [loc_size[i] / crop_size[i] for i in range(2)]
        cropped_tdata.append([str(x) for x in [
            td[0],
            *cropped_center_p[::-1],
            *loc_size_p[::-1]
        ]])
    empty = len(cropped_tdata) == 0
    written = False
    # not grayでかつannotationが無い場合は、100回に1回のみ保存する。grayは保存しない
    if not gray and (not empty or (not ignore_empty and ngemptyi % 100 == 0)):
        cropped_tfpath = f'{dpath}/cropped/{fnamewox}_{crop_index[0]}_{crop_index[1]}.txt'
        with open(cropped_tfpath, 'w') as f:
            f.write('\n'.join([' '.join(x) for x in cropped_tdata]))
        cropped_fpath = f'{dpath}/cropped/{fnamewox}_{crop_index[0]}_{crop_index[1]}.jpg'
        cv2.imwrite(cropped_fpath, cropped_im)
        written = True
    if not gray and empty:
        ngemptyi += 1
    return [empty, gray, written, ngemptyi]
dpath = os.path.dirname(os.path.realpath(__file__))
shutil.rmtree(f'{dpath}/cropped', ignore_errors=True)
os.makedirs(f'{dpath}/cropped')
crop_size = [640, 480]
overlap_size = [320, 240]
jpg_names = [p for p in os.listdir(f'{dpath}/all') if p[-4:] == '.jpg']
os.system(f'cp {dpath}/all/classes.txt {dpath}/cropped/')
ngemptyi = 0
emptyc = 0
totalc = 0
for ji, p in enumerate(jpg_names):
    print(f'{ji + 1} / {len(jpg_names)}')
    print(f'name: {p}')
    fpath = f'{dpath}/all/{p}'
    im = cv2.imread(fpath)
    size = im.shape[:2]
    if any([size[i] < crop_size[i] for i in range(2)]):
        print('image size too small')
        exit()
    crop_count = [(size[i] - crop_size[i] - 1) // overlap_size[i] + 2 for i in range(2)]
    print(f'crop count: {crop_count[0] * crop_count[1]}')
    cropped_ims = []
    for i in range(crop_count[0]):
        for j in range(crop_count[1]):
            crop_index = [i, j]
            max_size = [min([crop_index[k] * overlap_size[k] + crop_size[k], size[k]]) for k in range(2)]
            min_size = [max_size[k] - crop_size[k] for k in range(2)]
            cropped_im = np.copy(im[min_size[0]:max_size[0], min_size[1]:max_size[1]])
            # generate_tfrecordが失敗するためignore_emptyはとりあえずTrue←別原因だったので関係ないかも
            empty, gray, written, ngemptyi = write_cropped_im(dpath, p, size, crop_size, crop_index, min_size, cropped_im, ngemptyi, False)
            if written:
                totalc += 1
                if empty:
                    emptyc += 1
print(f'empty count: {emptyc}, total count: {totalc}')
