import os
import sys
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
    sys.path.append(parent_path)
import glob
from tqdm import tqdm
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Batch rename files.')
    parser.add_argument('--file-dir', type=str, help='Directory of files.')
    parser.add_argument('--save-dir', type=str, 
                        help='Save directory of output files (saves in the current directory if null).')
    parser.add_argument('--prefix', type=str, 
                        help='The prefix to the files to rename.')
    parser.add_argument('--start-idx', type=int, default=1, 
                        help='The start index of renamed files.')
    parser.add_argument('--target-type', type=str, default='jpg', 
                        help='Only rename files that have the target type.')

    return parser.parse_args()

def rename_files(file_dir, save_dir, prefix, start_idx, target_type):
    """Batch rename files of given type.

    Args:
        file_dir (str): The directory of files to rename.
        save_dir (str): The directory of renamed files (saves in the current directory if null).
        prefix (str): The prefix to the files to rename.
        start_idx (int):The start index of renamed files. 
        target_type (str): Only rename files that have the target type.
    """    
    
    if save_dir is not None and not os.path.exists(save_dir):
        os.makedirs(save_dir)

    pbar = tqdm(glob.glob('{0}/*.{1}'.format(file_dir, target_type)))
    for i, file_path in enumerate(pbar):
        if save_dir is not None:
            dst_file_path = os.path.join(save_dir, 
                                         '{0}_{1}.{2}'.format(prefix, start_idx+i, target_type))
        else:
            file_dir, _ = os.path.split(file_path)
            dst_file_path = os.path.join(file_dir, 
                                         '{0}_{1}.{2}'.format(prefix, start_idx+i, target_type))

        os.rename(file_path, dst_file_path)
        pbar.set_description('Renaming: {}'.format(dst_file_path))
    
if __name__ == '__main__':
    args = get_args()
    rename_files(args.file_dir, args.save_dir, args.prefix, args.start_idx, args.target_type)   
