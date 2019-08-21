#!/usr/bin/python3

import os
from os import path as osp
from sys import argv
import shutil

SCRIPTS = osp.dirname(__file__)
ROOT = osp.join(SCRIPTS, '..')
DEST = osp.join(ROOT, 'beano-public')

try:
    if osp.exists(DEST):
        shutil.rmtree(DEST)
    os.mkdir(DEST)
    with open(osp.join(SCRIPTS, 'client-closure.txt')) as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            trg = osp.join(ROOT, line)
            trg_dir = osp.dirname(trg)
            dst = osp.join(DEST, line)
            dst_dir = osp.dirname(dst)
            if dst_dir and not osp.exists(dst_dir):
                os.makedirs(dst_dir)
            print('copying from', trg, 'to', dst)
            shutil.copy2(trg, dst)
except OSError as e:
    print(e)
    print("Failed to create directory")
else:
    print("Successfully created directory")
