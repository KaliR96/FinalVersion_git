from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from constants import ADMIN_ID, CHANNEL_ID
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

    if not pending_reviews:
        await send_message(update, context, "Нет отзывов для модерации.", [["Админ меню🔙"]])
        context.user_data['state'] = 'admin_menu'
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
                 InlineKeyboardButton(f"Удалить🗑️", callback_data=f'delete_{review["message_id"]}')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await context.bot.send_message(chat_id=ADMIN_ID, text="Выберите действие:", reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Ошибка при пересылке сообщения: {e}")

    context.user_data['state'] = 'moderation_menu'


async def exit_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Отправляем сообщение об успешной обработке всех отзывов
    await send_message(update, context, "Все отзывы обработаны.", [["Админ меню🔙"]])
    context.user_data['state'] = 'admin_menu'

