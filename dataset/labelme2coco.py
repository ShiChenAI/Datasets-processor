import argparse
import collections
import datetime
import glob
import json
import os
import sys
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)
import uuid
import imgviz
import numpy as np
import labelme
from PIL import Image

try:
    import pycocotools.mask
except ImportError:
    print('Please install pycocotools:\n\n    pip install pycocotools\n')
    sys.exit(1)

def get_args():
    parser = argparse.ArgumentParser(description='Convert labelme annotations to coco fomat.')
    parser.add_argument('--input-dir', type=str, 
                        help='The input directory of annotations.')
    parser.add_argument('--output-dir', type=str, 
                        help='The output directory of coco fomat annotations.') 
    parser.add_argument('--dataset-type', type=str, 
                        help='The dataset type (train or val or test).')
    parser.add_argument('--cat-file', type=str, 
                        help='The file containing the categories names.')
    parser.add_argument('--noviz', action='store_true', 
                        help='No visualization.')
    args = parser.parse_args()

    return args

def convert_annotations(input_dir, output_dir, dataset_type, cat_file, noviz=False):
    """Convert labelme annotations to coco fomat.

    Args:
        input_dir (str): The input directory of annotations.
        output_dir (str): The output directory of coco format annotations.
        dataset_type (str): The dataset type (train or val or test).
        cat_file (str): The file containing the categories names.
        noviz (bool, optional): No visualization. Defaults to False.
    """    

    if not os.path.exists(output_dir):
        os.makedirs(os.path.join(output_dir, dataset_type))
    if not noviz and not os.path.exists(os.path.join(output_dir, 'Visualization')):
        os.makedirs(os.path.join(output_dir, 'Visualization'))
    print('Creating dataset:', output_dir)

    now = datetime.datetime.now()

    data = dict(info=dict(description=None,
                          url=None,
                          version=None,
                          year=now.year,
                          contributor=None,
                          date_created=now.strftime('%Y-%m-%d %H:%M:%S.%f'),),
                licenses=[dict(url=None, id=0, name=None,)],
                images=[
                        # license, url, file_name, height, width, date_captured, id
                       ],
                type='instances',
                annotations=[
                             # segmentation, area, iscrowd, image_id, bbox, category_id, id
                            ],
                categories=[
                            # supercategory, id, name
                           ],)
    
    cat_ids = {}
    for i, line in enumerate(open(cat_file).readlines()):
        cat_id = i - 1  # starts with -1
        cat_name = line.strip()
        if cat_id == -1:
            assert cat_name == '__ignore__'
            continue
        cat_ids[cat_name] = cat_id
        data['categories'].append(dict(supercategory=None, 
                                       id=cat_id, 
                                       name=cat_name,))
    
    out_ann_file = os.path.join(output_dir, '{}.json'.format(dataset_type))
    for img_id, filename in enumerate(glob.glob(os.path.join(input_dir, '*.json'))):
        print('Generating dataset from: ', filename)

        label_file = labelme.LabelFile(filename=filename)

        base = os.path.splitext(os.path.basename(filename))[0]
        out_img_file = os.path.join(output_dir, dataset_type, base + '.jpg')

        img = labelme.utils.img_data_to_arr(label_file.imageData)
        if img.shape[2] == 4: 
            #img = img[:, :, :3]
            img = Image.fromarray(img)
            img = img.convert('RGB')
            img = np.array(img)
        imgviz.io.imsave(out_img_file, img)
        data['images'].append(dict(license=0,
                                   url=None,
                                   file_name=os.path.relpath(out_img_file, 
                                                             os.path.dirname(out_ann_file)),
                                   height=img.shape[0],
                                   width=img.shape[1],
                                   date_captured=None,
                                   id=img_id,))

        masks = {}  # for area
        segmentations = collections.defaultdict(list)  # for segmentation
        for shape in label_file.shapes:
            points = shape['points']
            label = shape['label']
            group_id = shape.get('group_id')
            shape_type = shape.get('shape_type', 'polygon')
            mask = labelme.utils.shape_to_mask(img.shape[:2], points, shape_type)

            if group_id is None:
                group_id = uuid.uuid1()

            instance = (label, group_id)

            if instance in masks:
                masks[instance] = masks[instance] | mask
            else:
                masks[instance] = mask

            if shape_type == 'rectangle':
                (x1, y1), (x2, y2) = points
                x1, x2 = sorted([x1, x2])
                y1, y2 = sorted([y1, y2])
                points = [x1, y1, x2, y1, x2, y2, x1, y2]
            else:
                points = np.asarray(points).flatten().tolist()

            segmentations[instance].append(points)
        segmentations = dict(segmentations)

        for instance, mask in masks.items():
            cat_name, group_id = instance
            if cat_name not in cat_ids:
                continue
            cat_id = cat_ids[cat_name]

            mask = np.asfortranarray(mask.astype(np.uint8))
            mask = pycocotools.mask.encode(mask)
            area = float(pycocotools.mask.area(mask))
            bbox = pycocotools.mask.toBbox(mask).flatten().tolist()

            data['annotations'].append(dict(id=len(data['annotations']),
                                            image_id=img_id,
                                            category_id=cat_id,
                                            segmentation=[] if shape_type == 'rectangle' else segmentations[instance],
                                            area=area,
                                            bbox=bbox,
                                            iscrowd=0,))

        if not noviz:
            labels, captions, masks = zip(
                *[
                    (cat_ids[cnm], cnm, msk)
                    for (cnm, gid), msk in masks.items()
                    if cnm in cat_ids
                ]
            )
            viz = imgviz.instances2rgb(image=img,
                                       labels=labels,
                                       masks=masks,
                                       captions=captions,
                                       font_size=15,
                                       line_width=2,)
            out_viz_file = os.path.join(output_dir, 'Visualization', base + '.jpg')
            imgviz.io.imsave(out_viz_file, viz)

    with open(out_ann_file, 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    args = get_args()
    convert_annotations(args.input_dir, 
                        args.output_dir, 
                        args.dataset_type, 
                        args.cat_file,
                        args.noviz)