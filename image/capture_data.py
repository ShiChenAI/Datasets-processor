import os
import argparse
import cv2

def get_args():
    parser = argparse.ArgumentParser(description='Capture data (images/video) via camera.')
    parser.add_argument('--cam-id', type=int, default=0, help='Camera index.')
    parser.add_argument('--mode', type=int, default=0, 
                        help='0-visualization, 1-capturing images, 2-capturing video')
    parser.add_argument('--save-path', type=str, 
                        help='Save path to captured data.')
    parser.add_argument('--width', type=int, help='Image/video width.')
    parser.add_argument('--height', type=int, help='Image/video height.')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()

    cap = cv2.VideoCapture(args.cam_id)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if args.width == None else args.width
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if args.height == None else args.height
    fps = cap.get(cv2.CAP_PROP_FPS) 
    
    if args.mode == 0:
        print('Start visualization mode...')
    elif args.mode == 1:
        print('Start capturing images...')
        if not os.path.exists(args.save_path):
            os.makedirs(args.save_path)
    elif args.mode == 2:
        print('Start capturing video...')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        out = cv2.VideoWriter()
        out.open(args.save_path, fourcc, fps, (w, h), True)
    
    idx = 1
    while True:
        ret, frame = cap.read()
        cv2.imshow('Capture', frame)
        if args.mode == 1:
            file_name = os.path.join(args.save_path, '{}.png'.format(idx))
            cv2.imwrite(file_name, frame) 
            print('Saved image to ', file_name)
            idx += 1 
        elif args.mode == 2:
            out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    if args.mode == 2:
        out.release()