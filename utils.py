# utils.py

import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import logger, BASE_DIR

# Функция для отправки сообщения с кнопками
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, options: list) -> None:
    if isinstance(options[0], list):
        reply_markup = ReplyKeyboardMarkup(options, resize_keyboard=True, one_time_keyboard=True)
    else:
        reply_markup = ReplyKeyboardMarkup([options], resize_keyboard=True, one_time_keyboard=True)

    logger.info(f"Отправка сообщения с текстом: {message} и состоянием: {context.user_data.get('state', 'main_menu')}")

    await update.message.reply_text(message, reply_markup=reply_markup)

# Функция для отправки сообщения с inline-кнопками
async def send_inline_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, buttons: list) -> None:
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(message, reply_markup=keyboard)
    logger.info("Отправлено сообщение с кнопками: %s", message)

# Функция для получения пути к изображению по имени тарифа
def get_image_path(tariff_name):
    image_files = {
        'Ген.Уборка🧼': 'general.jpg',
        'Повседневная🧹': 'vacuumcat.png',
        'Послестрой🛠': 'build.jpg',
        'Мытье окон🧴': 'window.jpg'
    }

    image_file = image_files.get(tariff_name)
    if not image_file:
        raise ValueError(f"Изображение не найдено для тарифа: {tariff_name}")

    return os.path.join(BASE_DIR, 'img', image_file)

# Функция для получения описания тарифа
def get_description(tariff_name):
    from data import CLEANING_DETAILS

    details = CLEANING_DETAILS.get(tariff_name)
    if not details:
        raise ValueError(f"Описание не найдено для тарифа: {tariff_name}")

    return details['details_text']
