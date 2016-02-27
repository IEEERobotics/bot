import os

import unittest




filelist = os.listdir('test_images')

#Get all images
for f in filelist[:]:
    if not(f.endswith('.png')):
        filelist.remove(f)


for f in filelist:
    print f

