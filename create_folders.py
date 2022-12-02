import os
import sys
import shutil

input_folder = sys.argv[1]
output_folder = sys.argv[2]

filelist = os.listdir(input_folder)

urndict = dict()

for file in filelist:
    split = file.split('_')
    key = '_'.join(split[0:3])
    
    if key in urndict:
        urndict[key].append(file)
    else:
        urndict[key] = [file]

for key in urndict.keys():
    print(key)
    newdir = os.path.join(output_folder, key)
    os.makedirs(newdir)
    for file in urndict[key]:
        shutil.copy(os.path.join(input_folder, file), os.path.join(newdir, file))
