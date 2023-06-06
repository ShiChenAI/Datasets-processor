import os
import sys
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)
import json
import subprocess
import pandas as pd
from utils.dataset import coco2shape

class CocoDatasetHandler:
    def __init__(self, jsonpath, imgpath, shape='rectangle'):
        with open(jsonpath, 'r') as jsonfile:
            ann = json.load(jsonfile)
        self.shape = shape
        images = pd.DataFrame.from_dict(ann['images']).set_index('id')
        annotations = pd.DataFrame.from_dict(ann['annotations']).set_index('id')
        categories = pd.DataFrame.from_dict(ann['categories']).set_index('id')

        annotations = annotations.merge(images, left_on='image_id', right_index=True)
        annotations = annotations.merge(categories, left_on='category_id', right_index=True)
        annotations = annotations.assign(
            shapes=annotations.apply(self.coco2shape, axis=1))
        self.annotations = annotations
        
        self.labelme = {}

        self.imgpath = imgpath
        self.images = pd.DataFrame.from_dict(ann['images']).set_index('file_name')

    def coco2shape(self, row):
        if row.iscrowd == 1:
            shapes = self.rle2shape(row)
        elif row.iscrowd == 0:
            shapes = self.polygon2shape(row)
        return shapes

    def rle2shape(self, row):
        rle, shape = row['segmentation']['counts'], row['segmentation']['size']
        mask = self._rle_decode(rle, shape)
        padded_mask = np.zeros(
            (mask.shape[0]+2, mask.shape[1]+2),
            dtype=np.uint8,
        )
        padded_mask[1:-1, 1:-1] = mask
        points = find_contours(mask, 0.5)
        shapes = [
            [[int(point[1]), int(point[0])] for point in polygon]
            for polygon in points
        ]
        return shapes

    def _rle_decode(self, rle, shape):
        mask = np.zeros([shape[0] * shape[1]], np.bool)
        for idx, r in enumerate(rle):
            if idx < 1:
                s = 0
            else:
                s = sum(rle[:idx])
            e = s + r
            if e == s:
                continue
            assert 0 <= s < mask.shape[0]
            assert 1 <= e <= mask.shape[0], "shape: {}  s {}  e {} r {}".format(shape, s, e, r)
            if idx % 2 == 1:
                mask[s:e] = 1
        # Reshape and transpose
        mask = mask.reshape([shape[1], shape[0]]).T
        return mask

    def polygon2shape(self, row):
        # shapes: (n_polygons, n_points, 2)
        if self.shape == 'polygon':
            shapes = [
                [[int(points[2*i]), int(points[2*i+1])] for i in range(len(points)//2)]
                for points in row.segmentation
            ]
        elif self.shape == 'rectangle':
            shapes = [[row.bbox[0], row.bbox[1]], [row.bbox[0]+row.bbox[2], row.bbox[1]+row.bbox[3]]]
        return shapes

    def coco2labelme(self):
        fillColor = [255, 0, 0, 128]
        lineColor = [0, 255, 0, 128]

        groups = self.annotations.groupby('file_name')
        for file_idx, (filename, df) in enumerate(groups):
            print(filename)
            record = {
                'imageData': None,
                'fillColor': fillColor,
                'lineColor': lineColor,
                'imagePath': filename,
                'imageHeight': int(self.images.loc[filename].height),
                'imageWidth': int(self.images.loc[filename].width),
            }
            record['shapes'] = []

            instance = {
                'line_color': None,
                'fill_color': None,
                'shape_type': self.shape,
            }
            for inst_idx, (_, row) in enumerate(df.iterrows()):
                if self.shape == 'polygon':
                    for polygon in row.shapes:
                        copy_instance = instance.copy()
                        copy_instance.update({
                            'label': row['name'],
                            'group_id': inst_idx,
                            'points': polygon
                        })
                        record['shapes'].append(copy_instance)
                elif self.shape == 'rectangle':
                    copy_instance = instance.copy()
                    copy_instance.update({
                        'label': row['name'],
                        'group_id': None,
                        'points': row.shapes
                    })
                    record['shapes'].append(copy_instance)

            if filename not in self.labelme.keys():
                self.labelme[filename] = record

    def save_labelme(self, file_names, dirpath, save_json_only=False):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        else:
            raise ValueError(f"{dirpath} has existed")

        for file in file_names:
            filename = os.path.basename(os.path.splitext(file)[0])
            with open(os.path.join(dirpath, filename+'.json'), 'w') as jsonfile:
                json.dump(self.labelme[file], jsonfile, ensure_ascii=True, indent=2)
            if not save_json_only:
                subprocess.call(['cp', os.path.join(self.imgpath, file), dirpath])


ds = CocoDatasetHandler('/mnt/data/Dataset/safework/fukushima/FUKUSHIMA_coco/annotations/instances_val2020.json', '/mnt/data/Dataset/safework/fukushima/FUKUSHIMA_coco/val2020')
ds.coco2labelme()
ds.save_labelme(ds.labelme.keys(), '/mnt/data/Dataset/safework/fukushima/fukushima_labelme/val')
