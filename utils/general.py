import cv2
import os

class ImageReader(object):
    def __init__(self, file_names):
        self.file_names = file_names
        self.max_idx = len(file_names)

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        if self.idx == self.max_idx:
            raise StopIteration
        img = cv2.imread(self.file_names[self.idx], cv2.IMREAD_COLOR)
        if img.size == 0:
            raise IOError('Image {} cannot be read'.format(self.file_names[self.idx]))
        self.idx = self.idx + 1
        return self.file_names[self.idx - 1], img

class VideoReader(object):
    def __init__(self, file_name):
        self.file_name = file_name
        try:  # OpenCV needs int to read from webcam
            self.file_name = int(file_name)
        except ValueError:
            pass

    def __iter__(self):
        self.cap = cv2.VideoCapture(self.file_name)
        if not self.cap.isOpened():
            raise IOError('Video {} cannot be opened'.format(self.file_name))
        return self

    def __next__(self):
        was_read, img = self.cap.read()
        if not was_read:
            raise StopIteration
        return self.file_name, img

def get_file_list(file_dir):
    """Get the files in the directory and sort them in ascending order of file modification time.

    Args:
        file_dir (str): The directory of files.

    Returns:
        list: The sorted list of files in the directory.
    """    

    file_list = os.listdir(file_dir)

    return sorted(file_list, 
                  key=lambda x: os.path.getmtime(os.path.join(file_dir, x))) if file_list else []