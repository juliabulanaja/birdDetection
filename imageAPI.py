import random
import uuid
import configparser
from pathlib import Path

import cv2 
import numpy as np
from ultralytics import YOLO

config = configparser.ConfigParser()
config.read('config.ini')

DOWNLOADS_FOLDER = config['BOT']['DOWNLOADS_FOLDER']
PROCESSED_FOLDER = config['BOT']['PROCESSED_FOLDER']
MODEL_PARAMETER_PATH = config['BOT']['MODEL_PARAMETER_PATH']
test_folder_path = Path(config['BOT']['TEST_FOLDER_PATH'])

test_files = [p for p in list(test_folder_path.iterdir()) if p.suffix.lower() in ['.jpg']]

def create_session_list() -> list:
    return test_files.copy()


def choose_random_image(list: list) -> Path:
    random_image = random.choice(list)
    return random_image


def predict(image: Path) -> Path:
    image_name = image.name
    image_path = f'{PROCESSED_FOLDER}/{image_name}'

    model = YOLO(MODEL_PARAMETER_PATH)  # pretrained YOLO model
    predict_image = model(image)[0]  # return a list of Results objects  
    predict_image.save(filename=image_path)  # save to disk

    return image_path


def remove_file(file: Path) -> None:
    try:
        file_path = Path(file)
        file_path.unlink()
    except:
        pass


def save_file(resized_image_bytes: bytes) -> Path:
    file_name = f'{uuid.uuid4().hex}.jpg'
    file_path = Path(f'{PROCESSED_FOLDER}/{file_name}')
    with open(file_path, 'wb') as new_file:
        new_file.write(resized_image_bytes)

    return file_path


def resize_image(image_bytes: bytes, new_width: int, new_height: int) -> bytes:

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    resized_img = cv2.resize(img, (new_width, new_height))
    success, resized_image_bytes = cv2.imencode('.jpg', resized_img)
    resized_image_bytes = resized_image_bytes.tobytes()
    return resized_image_bytes


if __name__ == "__main__":
    ...
