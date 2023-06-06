import os
import sys
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)
import argparse
import glob
import random
from tqdm import tqdm
import shutil

def get_args():
    parser = argparse.ArgumentParser(description='Randomly select images.')
    parser.add_argument('--img-dir', type=str, 
                        help='Directory of images.')
    parser.add_argument('--save-dir', type=str, 
                        help='Save directory of output video file.')
    parser.add_argument('--n-samples', type=int, default=1, 
                        help='Number of samples.')
    parser.add_argument('--prefix', type=str, 
                        help='The prefix to the files to rename.')
    parser.add_argument('--start-idx', type=int, default=1, 
                        help='The start index of renamed files.')
    parser.add_argument('--target-type', type=str, default='jpg', 
                        help='Only sample files that have the target type.')

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    img_dir, save_dir, n_samples, prefix, start_idx, target_type = \
        args.img_dir, args.save_dir, args.n_samples, args.prefix, args.start_idx, args.target_type
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    src_img_paths = glob.glob('{0}/**/*.{1}'.format(img_dir, target_type))
    sel_samples = random.sample(src_img_paths, n_samples)
    
    pbar = tqdm(sel_samples)
    for i, src_path in enumerate(pbar):
        dest_path = os.path.join(save_dir, '{0}_{1}.{2}'.format(prefix, start_idx+i, target_type))
        shutil.copy(src_path, dest_path)
        pbar.set_description('Copyed to: {}'.format(dest_path))
