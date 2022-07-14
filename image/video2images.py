import os
import sys
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)
import cv2
import argparse

from utils.general import VideoReader

def get_args():
    parser = argparse.ArgumentParser(description='Video to images.')
    parser.add_argument('--video-source', type=str, 
                        help='Directory of videos/name of a video.')
    parser.add_argument('--save-dir', type=str, 
                        help='Save directory of output images.')
    parser.add_argument('--interval', type=int, default=1, 
                        help='Extracts images at the specified interval')

    return parser.parse_args()

def process_video(file_name, save_path, interval=1):
    """Convert a video file into a series of images.

    Args:
        file_name (str): The file name of video to convert.
        save_path (_type_): The path to save the converted images.
        interval (int, optional): Extracts images at the specified interval. Defaults to 1.
    """    

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    img_id = 1
    frame_provider = VideoReader(file_name)
    for i, (_, frame) in enumerate(frame_provider):
        if i == (img_id - 1) * interval:
            output_name = os.path.splitext(os.path.split(file_name)[1])[0] + '_{}.jpg'.format(img_id)
            output_path = os.path.join(save_path, output_name)
            cv2.imwrite(output_path, frame)
            img_id += 1
            print('Saved frame {}'.format(output_path))

if __name__ == '__main__':
    args = get_args()
    if os.path.isdir(args.video_source):
        for video_name in os.listdir(args.video_source):
            video_path = os.path.join(args.video_source, video_name)
            process_video(video_path, 
                          os.path.join(args.save_dir, 
                                       os.path.splitext(video_name)[0]), 
                                       args.interval)
    elif os.path.isfile(args.video_source):
        process_video(args.video_source, args.save_dir, args.interval)