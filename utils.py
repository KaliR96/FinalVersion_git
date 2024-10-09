from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, Update, InlineKeyboardButton, InputMediaPhoto
import os
from telegram import InputFile
from telegram.ext import ContextTypes
from constants import CLEANING_DETAILS
import logging

logger = logging.getLogger(__name__)

# Функция для отправки сообщения с обычными кнопками
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, options: list) -> None:
    try:
        # Проверяем, что `options` это список списков для правильного создания клавиатуры
        if isinstance(options[0], list):
            reply_markup = ReplyKeyboardMarkup(options, resize_keyboard=True, one_time_keyboard=True)
        else:
            # Если `options` - это просто список, преобразуем его в список списков
            reply_markup = ReplyKeyboardMarkup([options], resize_keyboard=True, one_time_keyboard=True)

        # Логируем отправку сообщения и текущее состояние пользователя
        logger.info(f"Отправка сообщения с текстом: {message} и состоянием: {context.user_data.get('state', 'main_menu')}")

        # Отправляем сообщение с кнопками
        await update.message.reply_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

# Функция для отправки сообщения с inline-кнопками
async def send_inline_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, buttons: list) -> None:
    try:
        keyboard = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(message, reply_markup=keyboard)

        # Логирование успешной отправки
        logger.info("Отправлено сообщение с inline-кнопками: %s", message)

    except Exception as e:
        logger.error(f"Ошибка при отправке inline сообщения: {e}")

# Функция для расчета стоимости уборки на основе площади
def calculate(price_per_sqm, sqm):
    total_cost = price_per_sqm * sqm

    # Проверка минимальной стоимости
    if total_cost < 1500:
        total_cost = 1500
        formatted_message = (
            f'Стоимость вашей уборки: 1500.00 руб.\n'
            'Это минимальная стоимость заказа.'
        )
    else:
        formatted_message = f'Стоимость вашей уборки: {total_cost:.2f} руб.'

    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }

# Функция для расчета стоимости мытья окон на основе количества створок
def calculate_windows(price_per_panel, num_panels):
    total_cost = price_per_panel * num_panels

    # Проверка минимальной стоимости
    if total_cost < 1500:
        total_cost = 1500
        formatted_message = (
            f'Стоимость мытья окон: 1500.00 руб.\n'
            'Это минимальная стоимость заказа.'
        )
    else:
        formatted_message = f'Стоимость мытья окон: {total_cost:.2f} руб. за {num_panels} створок(и).'

    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }

async def send_tariff_details(update: Update, context: ContextTypes.DEFAULT_TYPE, tariff: str) -> None:
    tariff_details = CLEANING_DETAILS.get(tariff)

    if not tariff_details:
        await update.message.reply_text("Извините, информация о тарифе не найдена.")
        return

    # Отправляем изображение тарифа
    image_path = tariff_details['image_path']
    if os.path.exists(image_path):
        with open(image_path, 'rb') as image_file:
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=InputFile(image_file))
    else:
        await update.message.reply_text("Изображение не найдено.")

    # Отправляем текстовые детали тарифа
    for detail in tariff_details['details_text']:
        await update.message.reply_text(detail)

