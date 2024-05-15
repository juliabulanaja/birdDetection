import configparser

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

config = configparser.ConfigParser()
config.read('config.ini')

DB_NAME = config['DB']['DB_NAME']
DB_PASSWORD = config['DB']['DB_PASSWORD']
DB_USERNAME = config['DB']['DB_USERNAME']
DB_HOST = config['DB']['DB_HOST']

engine = create_engine(f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
DBSession = sessionmaker(bind=engine)
session = DBSession()

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id= Column(Integer, nullable=True)
    image_to_predict = Column(String(250), nullable=True)
    is_downloaded = Column(Boolean, nullable=True)

Base.metadata.create_all(engine)
Base.metadata.bind = engine
