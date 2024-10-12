
from telegram import ReplyKeyboardMarkup, InputMediaPhoto
from utils import get_image_path, get_description

def send_cleaning_options(update, context):
    # Function to send cleaning options to the user
    options = [[key] for key in CLEANING_DETAILS.keys()]
    markup = ReplyKeyboardMarkup(options, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Выберите тип уборки:', reply_markup=markup)

def send_cleaning_details(update, context, service_type):
    # Function to send details of a cleaning service, including image and description
    image_path = get_image_path(service_type, CLEANING_DETAILS)
    description = get_description(service_type, CLEANING_DETAILS)
    if image_path:
        update.message.reply_photo(photo=open(image_path, 'rb'), caption=description)
    else:
        update.message.reply_text('Информация не найдена.')
