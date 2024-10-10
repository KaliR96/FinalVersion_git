from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from constants import ADMIN_ID, CHANNEL_ID
from menu_tree import MENU_TREE
from utils import send_message, send_inline_menu
import logging

logger = logging.getLogger(__name__)

# Функция для админ-панели
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_chat_id = update.message.chat_id

    # Проверка, является ли пользователь администратором
    if user_chat_id == ADMIN_ID:
        # Отправка админ-панели администратору
        await send_message(update, context, MENU_TREE['admin_menu']['message'], [["Модерация"]])
        context.user_data['state'] = 'admin_menu'
    else:
        # Если пользователь не админ, просто выводим главное меню для обычного пользователя
        await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])
        context.user_data['state'] = 'main_menu'


# Функция для модерации отзывов
async def moderate_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Модерирует отзывы."""
    pending_reviews = [review for review in context.application.bot_data.get('reviews', [])
                       if not review.get('approved', False) and not review.get('deleted', False)]

    if not pending_reviews:
        await send_message(update, context, "Нет отзывов для модерации.", [["Назад"]])
        context.user_data['state'] = 'moderation_menu'
        return

    for review in pending_reviews:
        try:
            # Пересылаем сообщение целиком для просмотра
            await context.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=review['user_id'],
                message_id=review['message_id']
            )

            # Добавляем инлайн-кнопки для модерации (опубликовать или удалить)
            buttons = [
                [InlineKeyboardButton(f"Опубликовать✅", callback_data=f'publish_{review["message_id"]}'),
                 InlineKeyboardButton(f"Удалить🗑️", callback_data=f'delete_{review["message_id"]}')],
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await context.bot.send_message(chat_id=ADMIN_ID, text="Выберите действие:", reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Ошибка при пересылке сообщения: {e}")

    # После обработки всех отзывов, добавляем только кнопку "Назад"
    await send_message(update, context, "Продолжайте модерацию:", [["Назад"]])
    context.user_data['state'] = 'moderation_menu'

async def save_review_to_bot_data(context, user_id, user_name, message_id, review_text):
    """
    Функция для сохранения отзыва в bot_data для дальнейшей модерации.
    """
    review_data = {
        'user_id': user_id,
        'user_name': user_name,
        'message_id': message_id,  # Используем message_id для пересылки сообщения
        'review': review_text,
        'approved': False,  # Отзыв по умолчанию не одобрен
        'deleted': False  # Отзыв по умолчанию не удален
    }

# Вставить эту функцию в admin.py или файл, где происходит модерация отзывов.
async def publish_review(context: ContextTypes.DEFAULT_TYPE, review: dict) -> None:
    try:
        # Если есть фото, пересылаем его в канал
        if review.get('photo_file_ids'):
            if len(review['photo_file_ids']) > 1:
                media_group = [InputMediaPhoto(photo_id) for photo_id in review['photo_file_ids']]
                await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
            else:
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=review['photo_file_ids'][0])

        # Пересылаем текст отзыва в канал
        await context.bot.forward_message(
            chat_id=CHANNEL_ID,
            from_chat_id=review['user_id'],
            message_id=review['message_id']
        )

        review['approved'] = True
        logger.info(f"Отзыв от {review['user_name']} успешно опубликован в канал.")
    except Exception as e:
        logger.error(f"Ошибка при публикации отзыва: {e}")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Не удалось опубликовать отзыв от {review['user_name']}. Ошибка: {e}")


async def exit_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Возвращает администратора в админ-меню."""
    await send_message(update, context, "Вы вышли из модерации.", [["Модерация"]])
    context.user_data['state'] = 'admin_menu'

