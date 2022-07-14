
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
