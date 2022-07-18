# Datasets-processor

## Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)

## Requirements
0. Python 3.x
1. opencv-python
2. Pillow
3. scikit-image
4. matplotlib
5. tqdm
6. pycocotools

## Installation
1. Clone this repository.
```
git clone git@github.com:ShiChenAI/Datasets-processor.git
cd Datasets-processor
```

2. Install the dependencies.
```
pip install -r requirements.txt
```

## Usage
### Image/video processing utilities.
1. Capture data via webcam by specifying camera ID, operation mode (visualize video only/save as images/save as a video), image height/weight.
```
python ./image/capture_data.py --cam-id 0 --mode 1 --save-path ./data/captures --width 1920 --height 1080
```

2. Convert video(s) to a series of images according to the specified interval.
```
python ./image/video2images.py --video-source ./data/videos --save-dir ./data/outputs/images --interval 10
```

3. Merge a series of images into a GIF file.
```
python ./image/images2gif.py --img-dir ./data/images --save-path ./data/outputs/merge.gif --width 480 --height 360 --duration 1
```

### Image datasets processing utilities.
1. Rename files of the specified type in the folder to ```{specified prefix}_{index}.{specified type}```.
```
python ./dataset/batch_rename.py --file-die ./data/images --save-dir ./data/outputs/images --prefix train --start-idx 1 --target-type jpg
```

2. Extract specified categories from the COCO datasets.
```
python ./dataset/coco_extract_cats.py --coco-dir ./data/coco --datasets train2014 val2014 --category-names person car --imgs-length 5000 --output-dir ./data/outputs/coco --vis-dir ./outputs/coco/vis
```

3. Convert dataset from VOC format to COCO format and split the dataset into train/val/test according to the specified split ratio.
```
python ./dataset/voc2coco.py --start-id 1 --images-dir ./data/voc2012/JPEGImages --annotations-dir ./data/voc2012/Annotations --output-dir ./data/outputs/coco --cat-file ./data/voc2012/category_names.txt --split-ratio 80 10 10
```
The organization of the file containing the category names is as follows:
```
person
car

...

```

4. Convert dataset from labelme format to COCO format.
```
python ./dataset/labelme2coco.py --input-dir ./data/labelme/annotations --output-dir ./data/outputs/coco --dataset-type train --cat-file ./data/labelme/category_names.txt --noviz
```
The organization of the file containing the category names is as follows:
```
__ignore__
_background_
person
car

...

```
