from telegram import Update  # Для обработки обновлений
from telegram.ext import ContextTypes  # Для работы с контекстом
from utils import send_message  # Для отправки сообщений
from menu_tree import MENU_TREE
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from constants import ADMIN_ID
import logging  # Для логирования

logger = logging.getLogger(__name__)


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает админ-панель."""

    # Логируем выбор администратора
    logger.info(f"Admin selected: {user_choice}")

    # Проверяем, выбрана ли опция в админ-панели
    if user_choice in MENU_TREE['admin_menu']['next_state']:
        next_state = MENU_TREE['admin_menu']['next_state'][user_choice]
        context.user_data['state'] = next_state

        # Если выбрана модерация, отправляем администратору сообщение
        if next_state == 'moderation_menu':
            await context.bot.send_message(chat_id=ADMIN_ID,
                                           text="Вы вошли в режим модерации отзывов. Вы можете просмотреть и управлять отзывами.")
            await send_message(update, context, MENU_TREE[next_state]['message'], MENU_TREE[next_state]['options'])
        else:
            # Обрабатываем остальные состояния
            await send_message(update, context, MENU_TREE[next_state]['message'], MENU_TREE[next_state]['options'])

    else:
        # Если команда не распознана
        await send_message(update, context, "Выберите корректную опцию в админ-панели.",
                           MENU_TREE['admin_menu']['options'])


async def moderation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_state: str) -> None:
    # Получаем все отзывы, которые ещё не обработаны
    pending_reviews = [review for review in context.application.bot_data.get('reviews', [])
                       if not review.get('approved', False) and not review.get('deleted', False)]

    if not pending_reviews:
        await send_message(update, context, "Нет отзывов для модерации.", MENU_TREE['admin_menu']['options'])
        context.user_data['state'] = 'admin_menu'
        return

    for review in pending_reviews:
        try:
            # Пересылаем сообщение целиком, используя сохраненный message_id
            await context.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=review['user_id'],
                message_id=review['message_id']  # Используем `message_id` для пересылки всего сообщения
            )

            buttons = [
                [InlineKeyboardButton(f"Опубликовать✅", callback_data=f'publish_{review["message_id"]}'),
                 InlineKeyboardButton(f"Удалить🗑️", callback_data=f'delete_{review["message_id"]}')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await context.bot.send_message(chat_id=ADMIN_ID, text="Выберите действие:", reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Ошибка при пересылке сообщения: {e}")

    context.user_data['state'] = 'moderation_menu'


