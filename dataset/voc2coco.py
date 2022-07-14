import os
import sys
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)
import argparse
import json
import xml.etree.ElementTree as ET
import shutil

from utils.general import get_xml_elements
from utils.dataset import get_dataset_type, get_category_ids
from utils.image import is_jpg

def get_args():
    parser = argparse.ArgumentParser('Convert dataset from voc format to coco format.')
    parser.add_argument('--start-id', type=int, default=1, 
                        help='start bounding box index.')
    parser.add_argument('--images-dir', type=str, 
                        help='image directory') 
    parser.add_argument('--annotations-dir', type=str, 
                        help='annotation directory') 
    parser.add_argument('--output-dir', type=str, 
                        help='output directory') 
    parser.add_argument('--cat-file', type=str, 
                        help='The file containing the categories names.')
    parser.add_argument('--split-ratio', nargs=3, type=int, default=[80, 10, 10], 
                        help='split ration of train/val/test dataset') 

    args = parser.parse_args()

    return args

def convert_annotations(start_id, images_dir, annotations_dir, 
                        output_dir, cat_file, split_ratio):
    """Convert voc annotations to coco fomat.

    Args:
        start_id (int): start bounding box index.
        images_dir (str): The input directory of images.
        annotations_dir (str): The input directory of annotations.
        output_dir (str): The output directory of coco fomat annotations.
        cat_file (str): The file containing the categories names.
        split_ratio (list): The split ration of train/val/test dataset.
    """    
    
    dest_ann_path = os.path.join(output_dir, 'annotations')
    if not os.path.exists(dest_ann_path):
        os.makedirs(dest_ann_path)

    json_info = {'train': {'file_name': os.path.join(dest_ann_path, 'instances_train.json'),
                           'dict': {'images':[], 
                                    'type': 'instances', 
                                    'annotations': [], 
                                    'categories': []}},
                 'val': {'file_name': os.path.join(dest_ann_path, 'instances_val.json'),
                         'dict': {'images':[], 
                                  'type': 'instances', 
                                  'annotations': [], 
                                  'categories': []}},
                 'test': {'file_name': os.path.join(dest_ann_path, 'instances_test.json'),
                          'dict': {'images':[], 
                                   'type': 'instances', 
                                   'annotations': [], 
                                   'categories': []}}}
    
    image_id = start_id
    bnd_id = start_id
    cat_ids = get_category_ids(cat_file)

    for _, _, xml_filenames in os.walk(annotations_dir):
        for xml_filename in xml_filenames:
            dataset_type = get_dataset_type(split_ratio)
            dest_img_dir = os.path.join(args.output_dir, dataset_type)
            
            if not os.path.exists(dest_img_dir):
                os.makedirs(dest_img_dir)
            
            xml_path = os.path.join(annotations_dir, xml_filename)
            tree = ET.parse(xml_path)
            root = tree.getroot()

            src_img_path = os.path.join(images_dir, root.find('filename').text)
            dest_img_path = os.path.join(dest_img_dir, '{}.jpg'.format(image_id))
            shutil.copy(src_img_path, dest_img_path)
            if not is_jpg(dest_img_path):
                os.remove(dest_img_path)
                continue

            has_cat = False
            for obj in get_xml_elements(root, 'object'):
                cat_name = get_xml_elements(obj, 'name', 1).text
                if cat_name not in cat_ids.keys():
                    continue
                has_cat = True

                category_id = cat_ids[cat_name]
                bndbox = get_xml_elements(obj, 'bndbox', 1)
                xmin = int(get_xml_elements(bndbox, 'xmin', 1).text) - 1
                ymin = int(get_xml_elements(bndbox, 'ymin', 1).text) - 1
                xmax = int(get_xml_elements(bndbox, 'xmax', 1).text)
                ymax = int(get_xml_elements(bndbox, 'ymax', 1).text)
                assert(xmax > xmin)
                assert(ymax > ymin)
                o_width = abs(xmax - xmin)
                o_height = abs(ymax - ymin)
                ann = {'area': o_width*o_height, 
                       'iscrowd': 0, 
                       'image_id': image_id, 
                       'bbox':[xmin, ymin, o_width, o_height],
                       'category_id': category_id, 
                       'id': bnd_id, 
                       'ignore': 0,
                       'segmentation': []}

                json_info[dataset_type]['dict']['annotations'].append(ann)
                bnd_id += 1

            if has_cat:
                size = get_xml_elements(root, 'size', 1)
                width = int(get_xml_elements(size, 'width', 1).text)
                height = int(get_xml_elements(size, 'height', 1).text)
                image = {'file_name': '{}.jpg'.format(image_id), 
                         'height': height, 
                         'width': width,
                         'id':image_id}

                json_info[dataset_type]['dict']['images'].append(image)
                image_id += 1
                print('Processed id: {0}, file name: {1}'.format(image_id, dest_img_path))

    for cat_name, cat_id in cat_ids.items():
        cat = {'supercategory': 'none', 
               'id': cat_id, 
               'name': cat_name}
        for dataset_type in json_info.keys():
            json_info[dataset_type]['dict']['categories'].append(cat)

    for dataset_type in json_info.keys():
        for cat_name, cat_id in cat_ids.items():
            cat = {'supercategory': 'none', 
                'id': cat_id, 
                'name': cat_name}
            json_info[dataset_type]['dict']['categories'].append(cat)    

        with open(json_info[dataset_type]['file_name'], 'w') as json_fp:
            json_str = json.dumps(json_info[dataset_type]['dict'])
            json_fp.write(json_str)

if __name__ == '__main__':
    args = get_args()
    convert_annotations(args.start_id, args.images_dir, args.annotations_dir, 
                        args.output_dir, args.cat_file, args.split_ratio)