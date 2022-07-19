import os
import sys
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)
import json
import subprocess
import pandas as pd
from utils.dataset import coco2shape

class Coco2LabelmeHandler:
    def __init__(self, jsonpath, imgpath):
        with open(jsonpath, 'r') as jsonfile:
            ann = json.load(jsonfile)

        images = pd.DataFrame.from_dict(ann['images']).set_index('id')
        annotations = pd.DataFrame.from_dict(ann['annotations']).set_index('id')
        categories = pd.DataFrame.from_dict(ann['categories']).set_index('id')

        annotations = annotations.merge(images, left_on='image_id', right_index=True)
        annotations = annotations.merge(categories, left_on='category_id', right_index=True)
        annotations = annotations.assign(shapes=annotations.apply(coco2shape, axis=1))
        self.annotations = annotations
        self.labelme = {}

        self.imgpath = imgpath
        self.images = pd.DataFrame.from_dict(ann['images']).set_index('file_name')

    def process(self):
        fillColor = [255, 0, 0, 128]
        lineColor = [0, 255, 0, 128]

        groups = self.annotations.groupby('file_name')
        for _, (filename, df) in enumerate(groups):
            record = {'imageData': None,
                      'fillColor': fillColor,
                      'lineColor': lineColor,
                      'imagePath': filename,
                      'imageHeight': int(self.images.loc[filename].height),
                      'imageWidth': int(self.images.loc[filename].width),}
            record['shapes'] = []

            instance = {'line_color': None,
                        'fill_color': None,
                        'shape_type': 'polygon',}
            for inst_idx, (_, row) in enumerate(df.iterrows()):
                for polygon in row.shapes:
                    copy_instance = instance.copy()
                    copy_instance.update({'label': row['name'],
                                          'group_id': inst_idx,
                                          'points': polygon})
                    record['shapes'].append(copy_instance)
            if filename not in self.labelme.keys():
                self.labelme[filename] = record

    def save(self, file_names, dirpath, save_json_only=False):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        else:
            raise ValueError('{} has existed'.format(dirpath))

        for file in file_names:
            filename = os.path.basename(os.path.splitext(file)[0])
            with open(os.path.join(dirpath, filename+'.json'), 'w') as jsonfile:
                json.dump(self.labelme[file], jsonfile, ensure_ascii=True, indent=2)
            if not save_json_only:
                subprocess.call(['cp', os.path.join(self.imgpath, file), dirpath])

"""
ds = Coco2LabelmeHandler('cocodataset/annotations/instances_train2014.json', 'cocodataset/train2014/')
ds.process()
ds.save(ds.labelme.keys(), 'cocodataset/labelme/train2014')
"""