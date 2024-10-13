from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import logger
from data import CLEANING_PRICES

# Функция для отправки сообщения с логированием
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

# Функция для расчета стоимости уборки
def calculate(price_per_sqm, sqm):
    total_cost = price_per_sqm * sqm
    if total_cost < 1500:
        total_cost = 1500
        formatted_message = 'Стоимость вашей уборки: 1500.00 руб.\nЭто минимальная стоимость заказа.'
    else:
        formatted_message = f'Стоимость вашей уборки: {total_cost:.2f} руб.'
    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }

# Функция для расчета стоимости мытья окон
def calculate_windows(price_per_panel, num_panels):
    total_cost = price_per_panel * num_panels
    if total_cost < 1500:
        total_cost = 1500
        formatted_message = 'Стоимость мытья окон: 1500.00 руб.\nЭто минимальная стоимость заказа.'
    else:
        formatted_message = f'Стоимость мытья окон: {total_cost:.2f} руб. за {num_panels} створок(и).'
    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }
