#!/usr/bin/env python3
""" Merge and process ImageJ ROI tables (read from csv files)

Processing:
    - assign Image (filename)
    - assign cropbox [x, y, x+w, y+h]
        - ensure 'Type' == 'Rectangle' (eg, not 'Composite')
    - assign uid

Handle cases: 
    * is passed a single file, not a list:
        - in this case, don't modify, just read as a df

Todo:
    * what to do if crop dir is not empty?
"""
import os
import pandas as pd
from glob import glob
import tifffile as tf

def merge_roi_lists(fname, save=True, outfile='roi_list_merged.csv'):
    """ Merge and process ImageJ ROI tables (read from csv files)
    
    Processing:
        - assign Image (filename)
        - assign cropbox [x, y, x+w, y+h]
            - ensure 'Type' == 'Rectangle' (eg, not 'Composite')
        - assign uid

    Handle cases: 
        * is passed a single file, not a list:
            - in this case, don't modify, just read as a df
        * rectify personal feelings about 'Image_Abspath'
    """
    def assign_columns(f, df):
        """ Skeleton to hold assignment functions
        """
        df = assign_image(f, df)
        df = assign_cropbox(df)
        df = assign_uid(df)
        return df

    def assign_image(f, df, ix=0):
        """ Not sure how much I like the Image_Abspath inclusion. Logic was
        in case the unambiguous name of the file needs to be resolved for 
        reasons.

        'Image' should be unambiguous enough in most cases, since if the file
        is run from a parent directory---shit, they'll contain dirsep
        characters. 

        TODO:
            * scheme to handle dirsep characters if script is running from
            parent dir
                - replace dirsep char << do this
                - take basename, change uid scheme?
        """
        if 'Image' not in df.columns:
            im = os.path.splitext(f)[0] + '.tif'
            df.insert(ix, 'Image', im)
            df['Image_Abspath'] = os.path.abspath(im)
        return df 

    def assign_cropbox(df, ix=0):
        def cropbox(row):
            """ Assign the cropbox to a row (one annotation) if the annotation
            is a rectangle. If it's a different shape, assign a cropbox of None
            --which will become 'NaN' if the table is read in by pd-- 
            (possible alt is to delete the row?  no)
            cropbox = [x, y, x+w, y+h]
            """
            if row['Type'] == 'Rectangle':
                cropbox = [row['X'], row['Y'], row['X'] + row['Width'], 
                        row['Y'] + row['Height']]
            else:
                # damnit I should set up a logger
                print('WARNING: The annotation "%s" (index %d) is not a \
                      rectangle!' %(row['Image'], row['Index']))
                cropbox = None
            return cropbox
        if 'Cropbox' not in df.columns:
            x = []
            for i in range(len(df)):
                x.append(cropbox(df.iloc[i]))
            df.insert(ix, 'Cropbox', x)
        return df

    def assign_uid(df, ix=0):
        """ uid will probably get used for/in the croped file name
        """
        def uid(row):
            im = os.path.splitext(row['Image'])[0]
            uid = '-'.join((row['Name'], im, str(row['Index'])))
            return uid
        # not sure if this if is needed, could just force assign the uid,
        # but maybe someone will manually edit them? Would that be sane?
        if 'UID' not in df.columns:
            x = []
            for i in range(len(df)):
                x.append(uid(df.iloc[i]))
            df.insert(ix, 'UID', x)
        return df

    if type(fname) == str:
        # We have a single 
        df = pd.read_csv(fname)
        df = assign_columns(fname, df)

    elif type(fname) == list:
        # We have multiple roi tables to merge
        df_ls = []
        for f in fname:
            df = pd.read_csv(f)
            df = assign_columns(f, df)
            df_ls.append(df)
        df = pd.concat(df_ls)
    else: 
        raise Exception('roi list filename was not of type string or list')

    if save:
        df.to_csv(outfile, index=False)
    return df

def tiffread(f):
    """ Read .tiff into numpy.ndarray
    Might be simpler than w/ libtiff. I'll note the catches I used to need 
    w/ libtiff just in case:
        - if reading a list, read a list of gs tifs and np.dstack (will do
        similar here)

    In
    --
    f : str or list, filename if gs or rgb, filenames if list of gs

    Out
    ---
    im : numpy.ndarray
    """
    if type(f) is str:
        # single image
        im = tf.imread(f)
        return im

    elif type(f) is list and len(f) == 3:
        # return rgb stack
        f.sort(reverse=True) # so r, g, b
        ims = [tf.imread(x) for x in f]
        return np.dstack(ims)
    else:
        raise ValueError("f must be a string or list of 3 strings")

def tiffwrite(filename, im):
    """ Write numpy.ndarray to tif.
    Might be simpler than w/ libtiff. I'll note the catches I used to need 
    w/ libtiff just in case:
        - need to distinguish b/t greyscale and rgb (write_rgb=True if shape 3)

    filename : str
    im : numpy.ndarray
    """
    tf.imwrite(filename, im)

def crop_images(row, crop_path):
    """ Crop annotation from image and save to it's label's dir
    row : series, a row from a pd.DataFrame
    """
    def crop(im, box, square=True):
        """ box: list, [x_left, y_bottom, x_l + w, y_b + h]
        """
        def pad_square(box):
            """ If box is a rectangle, expand it to a square.
            """
            x, y, xw, yh = box
            w = xw-x
            h = yh-y
            if w < h:
                w = h
            elif h < w:
                h = w
            return [x, y, x+w, y+h]
        if square:
            box = pad_square(box)
        x, y, xw, yh = box
        return im[y:yh, x:xw]
    im = tiffread(row['Image'])
    im_crop = crop(im, row['Cropbox'], square=True)
    crop_file = os.path.join(crop_path, row['Name'], row['UID'])
    tiffwrite(crop_file, im_crop)

### Main

def main(roi_csv, save_table=True, table_name='merged_roi_table.csv',
        crop_path='cropped'):
    """
    roi_csv : list or str, filename(s) of imagej roi table csv(s) to read
    save_table : bool, write roi table to a csv file
    merged_roi_csv : str, filename of the output table
    crop_path : str, path to save crops: 'crop_path/label/<croped_ims>'
    """
    df = merge_roi_lists(roi_csv, save=save_table, outfile=table_name)
    unique_labels = df['Name'].unique()
    for l in unique_labels:
        # TODO what if this path is not empty?
        path = os.path.join(crop_path, l)
        if not os.path.exists(path):
            os.makedirs(path)
    
    for i in range(len(df)):
        row = df.iloc[i]
        if type(row['Cropbox']) is list and len(row['Cropbox']) is 4:
            # then it probably isn't something unexpected
            crop_images(row, crop_path)

