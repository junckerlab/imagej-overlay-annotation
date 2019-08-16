#!/usr/bin/env python3
""" Display how many of each class there are in roi/annotation csvs. Would be
nice too if there is a check for duplicates.

In general, files named `merged_roi_table.csv` will contain a UID (for that
file) and Image_Abspath, so the script can be simpler if we stick to those ones
"""
import os
import pandas as pd
from glob import glob
import argparse
import re

def main(args):
    # Think that roi_files will always be a list due to nargs=+, but yolo
    if type(args.roi_files) == str or len(args.roi_files) == 0:
        df = pd.read_csv(args.roi_files)
    else:
        df = pd.concat([pd.read_csv(f) for f in args.roi_files])

    # Create a dataframe with the sure+maybes combined to get summary from 
    # Pair class names with their ? trimmed counterparts
    maybe_key = {name : re.sub('\?$', '', name) for name in df['Name'].unique()}
    df_less = df.replace(maybe_key)

    # Dict to hold results. More is cls and cls?. Less is cls = cls+cls?
    d = {k : summarize_classes(v) for k, v in zip(['more', 'less'], [df, df_less])}

    # Calculate the maybes for n objects
    metric = 'n_obj'
    x = pd.DataFrame(calc_maybes(d['more'], d['less'], metric))
    x = x.transpose()
    x = x.reindex(columns = ['yes', 'maybe', 'total'])
    print(x)

    return

def summarize_classes(df):
    cls = df['Name'].unique()
    d = {name: {} for name in cls}
    for name in cls:
         d[name]['n_obj'] = len(df[df['Name'] == name])
    return d

def calc_maybes(more, less, metric):
    d = {}
    for cls, v in less.items():
        total = less[cls][metric]
        try:
            yes = more[cls][metric]
        except KeyError:
            yes = 0
        maybe = total - yes
        d[cls] = {'yes': yes, 'maybe': maybe, 'total': total}
    return d

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('roi_files', nargs='+', 
                    help='One or more csv files to read and merge/crop from')
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
