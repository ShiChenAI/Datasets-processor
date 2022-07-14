from numpy import save
from pycocotools.coco import COCO
import os
import argparse
import shutil
from tqdm import tqdm
import skimage.io as io
import matplotlib.pyplot as plt
import cv2
from PIL import Image, ImageDraw

def get_args():
    parser = argparse.ArgumentParser('Extract specified categories from COCO.')
    parser.add_argument('--coco-dir', type=str, default='./coco2014')
    parser.add_argument('--datasets', type=str, nargs='+', default=['train2014', 'val2014'])
    parser.add_argument('--category-names', type=str, nargs='+', default=['person', 'car'])
    parser.add_argument('--imgs-length', type=int, default=5000)
    parser.add_argument('--output-dir', type=str, default='./outputs')
    parser.add_argument('--vis-dir', type=str, default='./outputs/temp')

    args = parser.parse_args()

    return args

headstr = """\
<annotation>
    <folder>VOC</folder>
    <filename>%s</filename>
    <source>
        <database>My Database</database>
        <annotation>COCO</annotation>
        <image>flickr</image>
        <flickrid>NULL</flickrid>
    </source>
    <owner>
        <flickrid>NULL</flickrid>
        <name>company</name>
    </owner>
    <size>
        <width>%d</width>
        <height>%d</height>
        <depth>%d</depth>
    </size>
    <segmented>0</segmented>
"""

objstr = """\
    <object>
        <name>%s</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>%d</xmin>
            <ymin>%d</ymin>
            <xmax>%d</xmax>
            <ymax>%d</ymax>
        </bndbox>
    </object>
"""

tailstr = '''\
</annotation>
'''

def id2name(coco):
    classes = dict()
    for cls in coco.dataset['categories']:
        classes[cls['id']] = cls['name']
    return classes

def get_objs(coco, img_id, coco_clses, clses_ids, clses_names):
    ann_ids = coco.getAnnIds(imgIds=img_id, catIds=clses_ids, iscrowd=None)
    anns = coco.loadAnns(ann_ids)

    objs = []
    for ann in anns:
        cls_name = coco_clses[ann['category_id']]
        if cls_name in clses_names:
            if 'bbox' in ann:
                bbox = ann['bbox']
                xmin = int(bbox[0])
                ymin = int(bbox[1])
                xmax = int(bbox[2] + bbox[0])
                ymax = int(bbox[3] + bbox[1])
                obj = [cls_name, xmin, ymin, xmax, ymax]
                objs.append(obj)

    return objs

def save_anns(file_name, src_img_path, dst_img_path, dst_ann_path, objs):
    shutil.copy(src_img_path, dst_img_path)
    img = cv2.imread(src_img_path)
    head = headstr % (file_name, img.shape[1], img.shape[0], img.shape[2])
    with open(dst_ann_path, 'w') as f:
        f.write(head)
        for obj in objs:
            f.write(objstr % (obj[0], obj[1], obj[2], obj[3], obj[4]))
        f.write(tailstr)

if __name__ == '__main__':
    args = get_args()

    for dataset in args.datasets:
        print('Processing dataset: {}'.format(dataset))

        ann_file = '{}/annotations/instances_{}.json'.format(args.coco_dir, dataset)
        ann_output_path = os.path.join(args.output_dir, 'annotations', dataset)
        if not os.path.exists(ann_output_path):
            os.makedirs(ann_output_path)
        img_output_path = os.path.join(args.output_dir, 'images', dataset)
        if not os.path.exists(img_output_path):
            os.makedirs(img_output_path)

        coco = COCO(ann_file)
        coco_clses = id2name(coco)
        clses_ids = coco.getCatIds(catNms=args.category_names)
        
        for cls_name in args.category_names:
            cls_id = coco.getCatIds(catNms=[cls_name])
            img_ids = coco.getImgIds(catIds=cls_id)
            img_ids = img_ids[:args.imgs_length] if len(img_ids) > args.imgs_length else img_ids
            print('Class: {}, includes {} images.'.format(cls_name, len(img_ids)))
            for img_id in tqdm(img_ids):
                img = coco.loadImgs(img_id)[0]
                file_name = img['file_name']
                img_path = os.path.join(args.coco_dir, dataset, file_name)
                objs = get_objs(coco, img_id, coco_clses, clses_ids, args.category_names)
                if len(objs) == 0:
                    continue
                
                dst_ann_path = os.path.join(ann_output_path, '{}.xml'.format(file_name[:-4]))
                dst_img_path = os.path.join(img_output_path, file_name)
                save_anns(file_name, img_path, dst_img_path, dst_ann_path, objs)

                if args.vis_dir is not None:
                    vis_path = os.path.join(args.vis_dir, dataset)
                    if not os.path.exists(vis_path):
                        os.makedirs(vis_path)
                    vis_img_path = os.path.join(vis_path, 'vis_{}'.format(file_name))

                    img = cv2.imread(img_path)
                    for obj in objs:
                        p1 = (obj[1], obj[2])
                        p2 = (obj[3], obj[4])
                        p3 = (max(obj[1], 15), max(obj[2], 15))
                        cv2.rectangle(img, p1, p2, (0, 0, 255), 2)
                        cv2.putText(img, obj[0], p3, cv2.FONT_ITALIC, 1, (0, 255, 0), 2)
                    
                    cv2.imwrite(vis_img_path, img)