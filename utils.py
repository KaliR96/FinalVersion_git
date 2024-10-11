import logging
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove


# Логирование
logger = logging.getLogger(__name__)

# Функция для отправки сообщений
async def send_message(update, context, message, options=None):
    """Отправляет сообщение с кнопками, если они есть."""
    # Создание клавиатуры с кнопками, если они есть, иначе удаление клавиатуры
    if options:
        reply_markup = ReplyKeyboardMarkup(options, resize_keyboard=True, one_time_keyboard=True)
    else:
        reply_markup = ReplyKeyboardRemove()  # Удаление кнопок, если их нет

    # Если сообщение пришло в обычной форме
    if update.message:
        # Логируем, что сообщение отправляется с определенными параметрами
        logger.info(f"Отправка сообщения: {message}, Кнопки: {options}")
        await update.message.reply_text(message, reply_markup=reply_markup)

    # Если сообщение пришло через callback_query (инлайн-кнопка)
    elif update.callback_query:
        logger.info(f"Отправка сообщения через callback: {message}, Кнопки: {options}")
        await update.callback_query.message.reply_text(message, reply_markup=reply_markup)
        await update.callback_query.answer()  # Закрываем callback

    # Если нет сообщения или callback, то логируем ошибку
    else:
        logger.warning("Не удалось отправить сообщение. Отсутствует 'message' или 'callback_query' в update.")


# Функция для отправки сообщения с inline-кнопками
async def send_inline_menu(update, context, message, options):
    buttons = [[InlineKeyboardButton(text=option, callback_data=option)] for option in options]
    reply_markup = InlineKeyboardMarkup(buttons)

    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(message, reply_markup=reply_markup)

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

