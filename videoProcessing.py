 
import os 
from pathlib import Path

import cv2 
import numpy as np


folder_path = Path('video/')   
extensions = ['.mov', '.mp4']
interval = 2000 
processed_folder_name = 'processedFrames1'


def get_frames(video, video_name, ms):

    # count the number of frames 
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    if not total_frames:
        return

    # frames per second
    fps = video.get(cv2.CAP_PROP_FPS)
    interval = int(fps / 1000 * ms)
    frames_m = np.arange(1, total_frames, interval)

    for f in frames_m: 

        video.set(cv2.CAP_PROP_POS_FRAMES, f)

        ret, frame = video.read()
        if not ret:
            continue

        name = f'./{processed_folder_name}/frame_{video_name}_{f}.jpg'
        print ('Creating...' + name) 

        frame = cv2.resize(frame, (512, 512))
        # writing the extracted images 
        cv2.imwrite(name, frame) 

    # Release all space and windows once done 
    video.release() 
    cv2.destroyAllWindows() 


def generate_frames_from_videos(interval=500):

    for file in list(folder_path.iterdir()):

        if not file.suffix.lower() in extensions:
            continue

        file_name = file.name  # name with extension
        folder_name = file.stem   # name without extension

        try: 
            
            # creating a folder named data 
            if not os.path.exists(f'{processed_folder_name}/'): 
                os.makedirs(f'{processed_folder_name}/') 
        
        # if not created then raise error 
        except OSError: 
            print ('Error: Creating directory of data') 


        cam = cv2.VideoCapture(f"video/{file_name}") 
    
        get_frames(cam, folder_name, interval)



if __name__ == '__main__':
    generate_frames_from_videos(interval=interval)
