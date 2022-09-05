import os
import imageio
from PIL import Image
from tqdm import tqdm
import cv2
from utils.general import get_file_list

def is_jpg(filename):
    """Check if the image format is jpg.

    Args:
        filename (str): The filename to check.

    Returns:
        bool: if the image format is jpg.
    """

    try:
        img = Image.open(filename)
        return img.format =='JPEG'
    except IOError:
        return False

def create_gif(save_path, img_dir, duration=0.1):
    """Create a gif file from images.

    Args:
        file_name (str): The name of the gif file to create.
        img_dir (str): The directory of the source images.
        duration (float, optional): The frame duration of the gif file. Defaults to 0.1.
    """    

    frames = [imageio.imread(os.path.join(img_dir, _)) for _ in get_file_list(img_dir)]
    imageio.mimsave(save_path, frames, 'GIF', duration=duration)

def convert_img(img_source, save_dir, img_size, target_type='png'):
    """Convert image(s) to specified type.

    Args:
        img_source (str): Directory of images/name of an image.
        save_dir (str): Save directory of output image(s).
        img_size (tuple): The size of output image(s)。
        target_type (str, optional): The target image type to convert. Defaults to 'png'.
    """    

    if os.path.isdir(img_source):
        pbar = tqdm(get_file_list(img_source))
        for img_name in pbar:
            img_path = os.path.join(img_source, img_name)
            if not os.path.isfile(img_path):
                continue
            pbar.set_description('Converting: {}'.format(img_path))
            img = Image.open(img_path)
            img.thumbnail((img_size))
            img.save(os.path.join(save_dir, 
                                  '{0}.{1}'.format(os.path.splitext(img_name)[0], 
                                                   target_type)))
    elif os.path.isfile(img_source):
        img = Image.open(img_source)
        img.thumbnail((img_size))
        img.save(os.path.join(save_dir, 
                              '{0}.{1}'.format(os.path.splitext(os.path.split(img_source)[1])[0], 
                                                                target_type)))

def create_video(save_path, img_dir, fps, img_size):
    """Create a video file from images.

    Args:
        file_name (str): The name of the video file to create.
        img_dir (str): The directory of the source images.
        fps (float): The frame rate of the video file.
        img_size (tuple): The size of converted images.
    """    

    fourcc = cv2.VideoWriter_fourcc('m','p','4', 'v')
    video  = cv2.VideoWriter(save_path, fourcc, fps, img_size)
    pbar = tqdm(get_file_list(img_dir))
    for img_name in pbar:
        img_path = os.path.join(img_dir, img_name)
        pbar.set_description('Processing: {}'.format(img_path))
        frame = cv2.imread(img_path)
        video.write(frame)

    video.release()
