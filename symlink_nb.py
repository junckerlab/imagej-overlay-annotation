#!/usr/bin/env python
""" Read image IDs from a txt file (positional arg) and symlink them to a
subdir (./nb) for more convinient annotation. The txt file should contain a
single file ID (eg 01, 04-2) on each line. Run this script from directory
containing the images.

Example file contents:

05
10
11

Useage:
    nb.py nb_file_ids.txt
"""
import os
from os.path import join as pj
from os.path import split as ps
import sys
import errno
from glob import glob
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=str, help='File containing im ids')
    parser.add_argument('-d', '--linkdir', type=str, default='nb', 
                        help='Name of the dir to create for symlinks (def: nb)')
    return parser.parse_args()

def force_symlink(src, dst):
    try:
        os.symlink(src, dst)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(dst)
            os.symlink(src, dst)
            return e

def main():
    args = parse_args()
    infile = args.infile
    copy_dir = args.linkdir
    glob_suffix = '-rgb*.tif' 

    with open(infile, 'r') as f:
        ids = [line.strip() for line in f]

    # Look for any permutations of each im ID

    if not os.path.exists(copy_dir):
        os.mkdir(copy_dir)

    for i in ids:
        for im in glob(i+glob_suffix):
            src = os.path.abspath(im)
            dst = pj(ps(src)[0], copy_dir, im)
            e = force_symlink(src, dst)

    if e:
        print('Overwrote prexisting symlinks!')

    print('Symlinked IDs in %s to %s' %(args.infile, args.linkdir))


main()
