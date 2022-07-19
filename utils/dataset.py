import numpy as np
from skimage.measure import find_contours
from utils.general import random_index

def get_dataset_type(split_ratio):
    """Randomly get the dataset type according to the specified probability.

    Args:
        split_ratio (list): The split ration of train/val/test dataset.

    Returns:
        str: The selected dataset type.
    """    

    dataset_types = ['train', 'val', 'test']
    return dataset_types[random_index(split_ratio)]

def get_category_ids(cat_file, no_background=True):
    """Get categories names and ids from a given file.

    Args:
        cat_file (str): The file containing the category names.
        no_background (bool, optional): VOC format does not contain the background category. 
                                        Defaults to True.
    
    Returns:
        dict: The category names and ids.
    """ 

    cat_ids = {}
    for i, line in enumerate(open(cat_file).readlines()):
        cat_id = i if no_background else i - 1
        cat_name = line.strip()
        if cat_id == -1:
            assert cat_name == '__ignore__'
            continue
        cat_ids[cat_name] = cat_id

    return cat_ids

def coco2shape(row):
    if row.iscrowd == 1:
        shapes = rle2shape(row)
    elif row.iscrowd == 0:
        shapes = polygon2shape(row)
    return shapes

def rle2shape(row):
    rle, shape = row['segmentation']['counts'], row['segmentation']['size']
    mask = rle_decode(rle, shape)
    padded_mask = np.zeros((mask.shape[0]+2, mask.shape[1]+2),
                            dtype=np.uint8,)
    padded_mask[1:-1, 1:-1] = mask
    points = find_contours(mask, 0.5)
    shapes = [[[int(point[1]), int(point[0])] for point in polygon]
              for polygon in points]
    return shapes

def rle_decode(rle, shape):
    mask = np.zeros([shape[0] * shape[1]], np.bool)
    for idx, r in enumerate(rle):
        s = 0 if idx < 1 else sum(rle[:idx])
        e = s + r
        if e == s:
            continue
        assert 0 <= s < mask.shape[0]
        assert 1 <= e <= mask.shape[0], 'shape: {}  s {}  e {} r {}'.format(shape, s, e, r)
        if idx % 2 == 1:
            mask[s:e] = 1

    # Reshape and transpose
    mask = mask.reshape([shape[1], shape[0]]).T
    return mask

def polygon2shape(row):
    # shapes: (n_polygons, n_points, 2)
    shapes = [[[int(points[2*i]), int(points[2*i+1])] for i in range(len(points)//2)]
              for points in row.segmentation]

    return shapes
