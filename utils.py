from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, Update, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ContextTypes
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
