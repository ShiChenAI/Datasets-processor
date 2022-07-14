import cv2
import os
import random

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

def random_index(rate):
    """Randomly select the category index based on the percentage probability.

    Args:
        rate (list): Percentage probability of each category.

    Returns:
        int: The selected index of the category.
    """

    start = 0
    index = 0
    randnum = random.randint(1, sum(rate))

    for index, scope in enumerate(rate):
        start += scope
        if randnum <= start:
            break

    return index

def get_xml_elements(root, tag, length=-1):
    """Get the corresponding elements in the xml tree based on a tag.

    Args:
        root (xml.etree.ElementTree.Element): The  the root element of the parsed xml tree.
        tag (str): The specified tag to retrieve corresponding elements.
        length (int, optional): The specified length. Defaults to -1.

    Returns:
        xml.etree.ElementTree.Element: Corresponding elements.
    """    
    
    vars = root.findall(tag)
    if len(vars) == 0:
        raise NotImplementedError('Can not find {0} in {1}.'.format(tag, root.tag))
    if length > 0 and len(vars) != length:
        raise NotImplementedError('The size of {0} is supposed to be {1}, but is {2}.'.format(tag, 
                                                                                              length, 
                                                                                              len(vars)))
    if length == 1:
        vars = vars[0]

    return vars