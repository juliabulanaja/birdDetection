import configparser
import requests
from pathlib import Path

import telebot
from telebot import types

from imageAPI import create_session_list, choose_random_image, predict, remove_file, save_file, resize_image
from dbAPI import add_record, get_image, get_is_downloaded

config = configparser.ConfigParser()
config.read('config.ini')

# Dictionary to track whether get_user_image has been called for each chat_id
image_processing_status = {}
buttons = {'select_button': types.InlineKeyboardButton('Select', callback_data='select_test_photo'),
           'find_button': types.InlineKeyboardButton('Try', callback_data='find_objects_in_photo'),
           'upload_button': types.InlineKeyboardButton('Upload', callback_data='upload_own_photo')
           }
TOKEN = config['TELEGRAM']['TELEGRAM_TOKEN']
MAX_FILE_SIZE = 3

bot = telebot.TeleBot(TOKEN)
image_list = create_session_list()
HELP_MESSAGE = """
Hi, I am your bird detection bird. 
Click SELECT button to try image of test dataset or UPLOAD button to upload your own image up to 3 mb. 
You can download only one image. If you upload multiple images, only first will be processed and other will be ignored.
"""

@bot.message_handler(commands=['help'])
def send_help_message(message: types.Message) -> None:
    markup = start_markup()
    bot.reply_to(message, HELP_MESSAGE, reply_markup=markup)


def start_markup() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(buttons['select_button'], buttons['upload_button'])
    return markup


def find_markup() -> types.InlineKeyboardMarkup:   
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(buttons['find_button'])
    return markup


def add_image_for_processing(chat_id: int, image: Path, downloaded: bool) -> None:
    add_record(chat_id, image, downloaded)


@bot.message_handler(commands=['start'])
def start(message: types.Message) -> None:

    chat_id = message.chat.id
    markup = start_markup()
    bot.send_message(chat_id, HELP_MESSAGE, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['select_test_photo', 'upload_own_photo'])
def handle_callback_query(call: types.CallbackQuery) -> None:

    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == 'select_test_photo':
        select_test_photo(call)
    elif call.data == 'upload_own_photo':
        upload_own_photo(call)

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)


@bot.callback_query_handler(func=lambda call: call.data == 'select_test_photo')
def select_test_photo(call: types.CallbackQuery) -> None:

    message = call.message
    chat_id = message.chat.id

    markup = find_markup()
    image = choose_random_image(image_list)
    add_image_for_processing(chat_id, image, False)
    bot.send_photo(chat_id, photo=open(image, 'rb'), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'find_objects_in_photo')
def find_objects_in_photo(call: types.CallbackQuery) -> None:

    chat_id  = call.message.chat.id
    message_id = call.message.message_id
    markup = start_markup()
    
    try: 
        image = get_image(chat_id)
    except KeyError:
        bot.send_message(chat_id, "Image haven't been choosen", reply_markup=markup)
        return
    
    try:
        predicted_file_path = predict(image)
    except FileNotFoundError:
        bot.send_message(chat_id, "Sorry, something went wrong. Choose another image.", reply_markup=markup)
        return
 
 
    bot.send_message(chat_id, 'Processed photo:')
    bot.send_photo(chat_id, photo=open(predicted_file_path, 'rb'), reply_markup=markup)
    remove_file(predicted_file_path)

    is_downloaded = get_is_downloaded(chat_id)

    if is_downloaded:
        remove_file(image)

    bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)


@bot.callback_query_handler(func=lambda call: call.data == 'upload_own_photo')
def upload_own_photo(call: types.CallbackQuery) -> None:
    message = call.message
    chat_id = message.chat.id

    # Reset the processing status for this chat_id
    image_processing_status[chat_id] = False

    msg = bot.send_message(chat_id, "Upload your image. Choose in menu 'Photo Or Video' and upload one image up to 3 mb with extension '.jpg', '.jpeg', '.png'. You can download only one image. If you upload multiple images, only first will be processed and other will be ignored. Waiting your image...")
    bot.register_next_step_handler(msg, get_user_image)



@bot.message_handler(content_types=['photo'])
def get_user_image(message: types.Message) -> None:

    chat_id = message.chat.id

    print("get_user_image called for chat_id:", chat_id)

    # Check if get_user_image has already been called for this chat_id
    if image_processing_status.get(chat_id, False):
        print("get_user_image already called for chat_id:", chat_id)
        return

    # Mark get_user_image as called for this chat_id
    image_processing_status[chat_id] = True
    

    try:
        # Extracting the file information
        photo = message.photo[-1]
        file_size = photo.file_size  # File size in bytes
        file_info = bot.get_file(message.photo[-1].file_id)
    except TypeError:
        markup = start_markup()
        bot.send_message(chat_id, "You've donloaded wrong format file. Choose in menu 'Photo Or Video' and upload image up to 3 mb with extension '.jpg', '.jpeg', '.png'.", reply_markup=markup)
        return
    
    # Check the file size 
    if file_size > MAX_FILE_SIZE * 1024 * 1024:
        markup = start_markup()
        bot.send_message(chat_id, f"Sorry, the file size exceeds the limit of {MAX_FILE_SIZE}MB.", reply_markup=markup)
        return

    markup = find_markup()

    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
    response = requests.get(file_url)

    if response.status_code == 200:

        resized_image_bytes = resize_image(response.content, 512, 512)
        file_path = save_file(resized_image_bytes)
        add_image_for_processing(chat_id, file_path, True)
        bot.send_message(chat_id, "You've downloaded your own image to test.")
        bot.send_message(chat_id, "Your image has been resized and saved.", reply_markup=markup)
  
    else:
        bot.send_message(chat_id, "Failed to download the image.")

  
bot.polling()
