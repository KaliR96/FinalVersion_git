from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from utils import send_message
from menu_tree import MENU_TREE
from constants import CHANNEL_ID, ADMIN_ID
import logging

logger = logging.getLogger(__name__)

# Функция для модерации отзывов
async def moderate_reviews(update, context, user_state):
    # Получаем все отзывы, которые еще не обработаны (не опубликованы и не удалены)
    pending_reviews = [review for review in context.application.bot_data.get('reviews', [])
                       if not review.get('approved', False) and not review.get('deleted', False)]

    if not pending_reviews:
        # Если нет отзывов для модерации, отправляем сообщение админу
        await send_message(update, context, "Нет отзывов для модерации.", MENU_TREE['admin_menu']['options'])
        context.user_data['state'] = 'admin_menu'
        return

    for review in pending_reviews:
        try:
            # Проверяем, что у отзыва есть необходимые данные
            if 'message_id' not in review or 'user_id' not in review:
                logger.error(f"Недостаточные данные для отзыва: {review}")
                continue  # Пропускаем отзыв без нужных данных

            # Пересылаем сообщение целиком, используя сохраненный message_id
            await context.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=review['user_id'],
                message_id=review['message_id']  # Используем message_id для пересылки сообщения
            )

            # Создаем кнопки для модерации отзыва
            buttons = [
                [InlineKeyboardButton(f"Опубликовать✅", callback_data=f'publish_{review["message_id"]}'),
                 InlineKeyboardButton(f"Удалить🗑️", callback_data=f'delete_{review["message_id"]}')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)

            # Отправляем сообщение с кнопками администратору
            await context.bot.send_message(chat_id=ADMIN_ID, text="Выберите действие:", reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Ошибка при пересылке сообщения с message_id {review['message_id']}: {e}")

    # Устанавливаем состояние пользователя для модерации
    context.user_data['state'] = 'moderation_menu'


# Функция для публикации отзыва
async def publish_review(context, review):
    try:
        # Если в отзыве есть фотографии
        if review.get('photo_file_ids'):
            if len(review['photo_file_ids']) > 1:
                # Если больше одной фотографии, отправляем как media group
                media_group = [InputMediaPhoto(photo_id) for photo_id in review['photo_file_ids']]
                await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
            else:
                # Если одна фотография, отправляем как фото
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=review['photo_file_ids'][0])

        # Пересылаем оригинальное сообщение от пользователя в канал
        await context.bot.forward_message(
            chat_id=CHANNEL_ID,
            from_chat_id=review['user_id'],
            message_id=review['message_id']
        )

        # Обновляем статус отзыва как "опубликован"
        review['approved'] = True
        logger.info(f"Отзыв от {review['user_name']} (message_id: {review['message_id']}) успешно опубликован в канал.")

    except Exception as e:
        # Логируем и отправляем сообщение администратору о проблеме с публикацией
        logger.error(f"Ошибка при публикации отзыва (message_id: {review.get('message_id')}): {e}")
        await context.bot.send_message(chat_id=ADMIN_ID,
                                       text=f"Не удалось опубликовать отзыв от {review['user_name']}. Ошибка: {e}")
