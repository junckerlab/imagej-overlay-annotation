- [`merge_roi_lists.py`](#merge_roi_lists)
- [`symlink_nb.py`](#symlink_nb)

----
# symlink_nb

Read image IDs from a txt file (positional arg) and symlink them to a
subdir (./nb) for more convinient annotation. The txt file should contain a
single file ID (eg 01, 04-2) on each line. Run this script from directory
containing the images.

Example file contents:
```
05
10
11
```

Useage: `nb.py nb_file_ids.txt`

----
# merge_roi_lists
Merge and process ImageJ ROI tables (read from csv files)

### Processing:
- assign Image (filename)
- assign cropbox [x, y, x+w, y+h]
  - ensure 'Type' == 'Rectangle' (eg, not 'Composite')
- assign uid

### Handle cases: 
- is passed a single file, not a list:
  - in this case, don't modify, just read as a df

## workflow for ij annotation using overlays

1. Open ROI manager 
2. Rectangular selection
3. Add to roi [t]
3. From here either add additional selections and then rename/label in bulk, or add each label as it comes
4. rename rois to labels
5. save roi list table (macro)
6. overlay from roi manager (macro, doesn't always work)
7. save image (i.e., save image w/ overlay)

## Overlays in ImageJ

`Image > Overlay > Add Selection`

## Cautions:
- There is only one overlay » adding a _New overlay_ will result in the
  destruction of your current one
- TIFF is the only format that supports overlays
  - TIFFs support overlays, this is good to know
- You can't really edit the overlay, make a mistake » need to start over
  - Recommended to build up overlays in ROI manager first to get them "just
    right" before `Image » Overlay » From ROI Manager`
  - Also note: `Image » Overlay » To ROI Manager`
    - » removes everthing from overlay and places into ROI
- Toggle w/ `Hide Overlay` **not Remove Overlay**

## Notes
- ROI manager: `more » labels » use names as labels`
  - macro recorder was not aware of this
- <C-S-y>: overlay options
