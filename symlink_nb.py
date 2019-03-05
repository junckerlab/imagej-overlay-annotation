#!/usr/bin/env python
""" Read image IDs from a txt file (positional arg) and symlink them to a
subdir (./nb) for more convinient annotation. The txt file should contain a
single file ID (eg 01, 04-2) on each line. Run this script from directory
containing the images.

Useage:
    nb.py nb_file_ids.txt
"""
import os
from os.path import join as pj
from os.path import split as ps
import sys
import errno

infile = sys.argv[1]
copy_dir = "./nb"

with open(infile, 'r') as f:
    ids = [line.strip() +'-rgb.tif' for line in f]

if not os.path.exists(copy_dir):
    os.mkdir(copy_dir)

def force_symlink(src, dst):
    try:
        os.symlink(src, dst)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(dst)
            os.symlink(src, dst)

try:
    for i in ids:
        src = os.path.abspath(i)
        dst = pj(ps(src)[0], copy_dir, i)
        force_symlink(src, dst)
    print('Created symlinks for file IDs in', infile)
except:
    print('BIG PROBLEM: failed to create symlinks')
