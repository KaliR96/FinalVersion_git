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
    pending_reviews = [review for review in context.application.bot_data.get('reviews', [])
                       if not review.get('approved', False) and not review.get('deleted', False)]

    if not pending_reviews:
        await send_message(update, context, "Нет отзывов для модерации.", [])
        return

    for review in pending_reviews:
        try:
            await context.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=review['user_id'],
                message_id=review['message_id']
            )

            buttons = [
                [InlineKeyboardButton(f"Опубликовать✅", callback_data=f'publish_{review["message_id"]}'),
                 InlineKeyboardButton(f"Удалить🗑️", callback_data=f'delete_{review["message_id"]}')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await context.bot.send_message(chat_id=ADMIN_ID, text="Выберите действие:", reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Ошибка при пересылке сообщения: {e}")

# Обработка нажатия инлайн-кнопок для модерации
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_state = context.user_data.get('state', 'main_menu')

    # Обрабатываем действия по модерации
    if user_state == 'moderation_menu':
        action, message_id = query.data.split('_')
        pending_reviews = context.application.bot_data.get('reviews', [])
        review = next((r for r in pending_reviews if str(r['message_id']) == message_id), None)

        if review:
            if action == 'delete':
                review['deleted'] = True
                await query.edit_message_text(text="Отзыв удален.")
                context.application.bot_data['reviews'].remove(review)
            elif action == 'publish':
                review['approved'] = True
                await publish_review(context, review)
                await query.edit_message_text(text="Отзыв опубликован.")

        remaining_reviews = [r for r in pending_reviews if not r.get('approved', False) and not r.get('deleted', False)]
        if not remaining_reviews:
            await context.bot.send_message(chat_id=ADMIN_ID, text="Все отзывы обработаны.")
            context.user_data['state'] = 'admin_menu'
            return

# Публикация отзыва
async def publish_review(context: ContextTypes.DEFAULT_TYPE, review: dict) -> None:
    try:
        await context.bot.forward_message(
            chat_id=CHANNEL_ID,
            from_chat_id=review['user_id'],
            message_id=review['message_id']
        )
        review['approved'] = True
        logger.info(f"Отзыв от {review['user_name']} опубликован.")
    except Exception as e:
        logger.error(f"Ошибка при публикации отзыва: {e}")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Не удалось опубликовать отзыв: {e}")
