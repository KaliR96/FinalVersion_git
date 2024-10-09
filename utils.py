import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Логирование
logger = logging.getLogger(__name__)

# Функция для отправки сообщений
async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, options: list) -> None:
    # Проверяем, что `options` это список списков
    if isinstance(options[0], list):
        reply_markup = ReplyKeyboardMarkup(options, resize_keyboard=True, one_time_keyboard=True)
    else:
        # Если `options` - это просто список, преобразуем его в список списков
        reply_markup = ReplyKeyboardMarkup([options], resize_keyboard=True, one_time_keyboard=True)

    # Логируем отправку сообщения и состояние
    logger.info(f"Отправка сообщения с текстом: {message} и состоянием: {context.user_data.get('state', 'main_menu')}")

    await update.message.reply_text(message, reply_markup=reply_markup)

# Функция для отправки сообщения с inline-кнопками
async def send_inline_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, buttons: list) -> None:
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(message, reply_markup=keyboard)
    logger.info("Отправлено сообщение с кнопками: %s", message)

# Функция для расчета стоимости уборки (оригинальное название - calculate)
def calculate(price_per_sqm, square_meters):
    """Рассчитывает стоимость уборки на основе цены за квадратный метр и общей площади."""
    total_cost = price_per_sqm * square_meters

    # Проверка минимальной стоимости
    if total_cost < 1000:
        total_cost = 1000
        formatted_message = (
            f'Стоимость уборки: 1000.00 руб.\n'
            'Это минимальная стоимость заказа.'
        )
    else:
        formatted_message = f'Стоимость уборки: {total_cost:.2f} руб.'

    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }

# Функция для расчета стоимости мытья окон
def calculate_windows(price_per_panel, num_panels):
    """Рассчитывает стоимость мытья окон на основе количества створок и цены за створку."""
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



# async def send_tariff_details(update: Update, context: ContextTypes.DEFAULT_TYPE, tariff: str) -> None:
#     tariff_details = CLEANING_DETAILS.get(tariff)
#
#     if not tariff_details:
#         await update.message.reply_text("Извините, информация о тарифе не найдена.")
#         return
#
#     # Отправляем изображение тарифа
#     image_path = tariff_details['image_path']
#     if os.path.exists(image_path):
#         with open(image_path, 'rb') as image_file:
#             await context.bot.send_photo(chat_id=update.message.chat_id, photo=InputFile(image_file))
#     else:
#         await update.message.reply_text("Изображение не найдено.")
#
#     # Отправляем текстовые детали тарифа
#     for detail in tariff_details['details_text']:
#         await update.message.reply_text(detail)

