import os
dpath = os.path.dirname(os.path.realpath(__file__))
tnames = [p for p in os.listdir(f'{dpath}/all') if p[-4:] == '.txt']
matnames = []
for tname in tnames:
    if tname == 'classes.txt':
        continue
    fpath = f'{dpath}/all/{tname}'
    lines = None
    with open(fpath) as f:
        lines = f.read().strip().split('\n')
    if len(lines) > 1:
        matnames.append(tname)
with open(f'{dpath}/multi_annot_files.txt', 'w') as f:
    f.write('\n'.join(matnames))
