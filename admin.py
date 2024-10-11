from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from constants import ADMIN_ID
from menu_tree import MENU_TREE
from utils import send_message
import logging

logger = logging.getLogger(__name__)

# Функция для админ-панели
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_chat_id = update.message.chat_id

    # Проверка, является ли пользователь администратором
    if user_chat_id == ADMIN_ID:
        # Отправка админ-панели администратору
        await send_message(update, context, MENU_TREE['admin_menu']['message'], MENU_TREE['admin_menu']['options'])
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

    # Логируем количество отзывов для модерации
    logger.info(f"Найдено {len(pending_reviews)} отзывов для модерации.")

    if not pending_reviews:
        await send_message(update, context, "Нет отзывов для модерации.", [["Назад"]])
        context.user_data['state'] = 'moderation_menu'
        return

    for review in pending_reviews:
        try:
            logger.info(f"Пересылка отзыва от {review['user_name']} админу.")
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
            logger.error(f"Ошибка при пересылке сообщения админу: {e}")

    # После обработки всех отзывов, добавляем только кнопку "Назад"
    await send_message(update, context, "Продолжайте модерацию:", [["Назад"]])
    context.user_data['state'] = 'moderation_menu'


async def exit_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Отправляем сообщение об успешной обработке всех отзывов
    await send_message(update, context, "Все отзывы обработаны.", [["Админ меню🔙"]])
    context.user_data['state'] = 'admin_menu'

async def save_review_to_bot_data(context, user_id, user_name, message_id, review_text, media_file_ids=None):
    """Сохраняет отзыв в бот-данные для последующей модерации."""
    review_data = {
        'user_id': user_id,
        'user_name': user_name,
        'message_id': message_id,
        'review': review_text,
        'photo_file_ids': media_file_ids if media_file_ids else [],
        'approved': False,  # Отзыв еще не одобрен
        'deleted': False    # Отзыв еще не удален
    }

    # Сохраняем данные отзыва в context.application.bot_data
    if 'reviews' not in context.application.bot_data:
        context.application.bot_data['reviews'] = []

    context.application.bot_data['reviews'].append(review_data)
    logger.info(f"Отзыв от {user_name} с медиафайлами сохранен для модерации.")



