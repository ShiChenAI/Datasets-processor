import os
import sys
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)
import shutil
import argparse

from utils.image import create_video, convert_img

def get_args():
    parser = argparse.ArgumentParser(description='Images to gif.')
    parser.add_argument('--img-dir', type=str, 
                        help='Directory of images.')
    parser.add_argument('--save-path', type=str, 
                        help='Save path of output video file.')
    parser.add_argument('--width', type=int, default=480, 
                        help='Images width.')
    parser.add_argument('--height', type=int, default=360, 
                        help='Images height.')
    parser.add_argument('--fps', type=int, default=30, 
                        help='Frame rate.')

    return parser.parse_args()

def process_images(img_dir, save_path, fps, img_size):
    """Convert images to a video file.

    Args:
        img_dir (str): The directory of images.
        save_path (str): The sace path of created gif file.
        fps (float): The frame rate of the video file.
        img_size (tuple): The size of converted images.
    """    

    temp_dir = os.path.join(os.path.split(save_path)[0], 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    save_dir = os.path.split(save_path)[0]
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    print('Start conveting images...')
    convert_img(img_dir, temp_dir, img_size)
    print('Start creating video file...')
    create_video(save_path, temp_dir, fps, img_size)
    shutil.rmtree(temp_dir)

if __name__ == '__main__':
    args = get_args()
    save_path = os.path.join(args.img_dir, '{}.mp4'.format(os.path.basename(args.img_dir))) \
                if not args.save_path else args.save_path

    process_images(args.img_dir, save_path, args.fps, (args.width, args.height))