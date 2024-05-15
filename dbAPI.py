import configparser
from pathlib import Path

from createDB import Users, session

config = configparser.ConfigParser()
config.read('config.ini')

DB_NAME = config['DB']['DB_NAME']
DB_PASSWORD = config['DB']['DB_PASSWORD']
DB_USERNAME = config['DB']['DB_USERNAME']
DB_HOST = config['DB']['DB_HOST']


def add_record(chat_id: int, image: Path, downloaded: bool):
    image = str(image)
    user = session.query(Users).filter(Users.chat_id == chat_id).scalar()

    if not user:
        user = Users(chat_id=chat_id, image_to_predict=image, is_downloaded=downloaded)
    else:
        user.image_to_predict = image
        user.is_downloaded = downloaded

    session.add(user)
    session.commit()

def get_image(chat_id: int):
    user = session.query(Users).filter(Users.chat_id == chat_id).scalar()
    session.commit()
    image_path = Path(user.image_to_predict)
    return image_path

def get_is_downloaded(chat_id: int):
    user = session.query(Users).filter(Users.chat_id == chat_id).scalar()
    session.commit()
    return user.is_downloaded


if __name__ == "__main__":      
   ...
