from lib2to3.pytree import convert
import os
from webbrowser import get
import imageio
from PIL import Image
from tqdm import tqdm
from utils.general import get_file_list

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
    """COnvert image(s) to specified type.

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