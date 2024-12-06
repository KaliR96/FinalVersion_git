from telegram import Update, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from config import ADMIN_ID, CHANNEL_ID, logger
from data import CLEANING_PRICES, CLEANING_DETAILS
from database import execute_query
from menu import MENU_TREE
from utils import send_message, send_inline_message, calculate_windows
from analytics import get_summary_by_period
from analytics import track_event, check_user_in_database


async def analytics_menu(update, context):
    summary = await get_summary_by_period('1 day')
    report = "\n".join([f"{state}: {count}" for state, count in summary])
    await update.message.reply_text(f"Статистика за день:\n{report}")


async def check_user_in_database(user_id):
    query = "SELECT EXISTS(SELECT 1 FROM user_analytics WHERE user_id = ?);"
    result = await execute_query(query, (user_id,))
    return result[0][0] == 1

# Пример отправки сообщения с логированием
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Получаем данные пользователя
    user = update.message.from_user
    user_id = user.id
    username = user.username or "Anonymous"
    user_state = context.user_data.get('state', 'main_menu')
    user_choice = update.message.text.strip() if update.message and update.message.text else None

    # Логируем текущее состояние
    logger.info("Текущее состояние: %s", user_state)

    # Добавляем трекинг события для каждого действия
    await track_event(
        user_id=user_id,
        username=username,
        state=user_state,
        is_new=False  # Предполагаем, что пользователь уже проверен в "start"
    )

    # Переход на состояние "Полезная информация📢"
    if user_choice == 'Полезная информация📢':
        context.user_data['state'] = 'useful_info'
        await show_useful_info(update, context)
        return

    if user_state == 'write_review':
        # Сохраняем отзыв
        review_text = update.message.caption or update.message.text or ""
        message_id = update.message.message_id
        user_name = update.message.from_user.full_name

        if review_text == MENU_TREE['write_review']['options'][0]:
            await send_message(update, context, "Главное меню", MENU_TREE['main_menu']['options'])
            context.user_data['state'] = 'main_menu'
            return
        elif review_text == '':
            review_data = {
                'review': review_text,
                'user_name': user_name,
                'user_id': user_id,
                'message_id': message_id,
                'approved': False
            }

            context.application.bot_data.setdefault('reviews', []).append(review_data)
            context.user_data['state'] = 'write_review'
            return
        else:
            review_data = {
                'review': review_text,
                'user_name': user_name,
                'user_id': user_id,
                'message_id': message_id,
                'approved': False
            }

            context.application.bot_data.setdefault('reviews', []).append(review_data)
            await send_message(update, context, "Спасибо за ваш отзыв! Он будет добавлен через некоторое время.",
                               MENU_TREE['write_review']['options'])
            context.user_data['state'] = 'write_review'
            return

    # Обработка нажатия кнопки "Посмотреть Отзывы💬"
    if user_state == 'reviews_menu' and user_choice == 'Посмотреть Отзывы💬':
        channel_url = "https://t.me/CleaningSphere"  # Замените на реальную ссылку на канал
        await update.message.reply_text(f"Просмотрите все отзывы на нашем канале: {channel_url}")
        context.user_data['state'] = 'main_menu'
        return

    # Обработка нажатия кнопки "Назад" при показе тарифов
    if user_state.startswith('detail_') and user_choice == 'Назад':
        context.user_data['state'] = 'show_tariffs'
        await send_message(update, context, MENU_TREE['show_tariffs']['message'], MENU_TREE['show_tariffs']['options'])
        return

    # Логика для администратора
    if user_id == ADMIN_ID:
        if user_state == 'main_menu':
            context.user_data['state'] = 'admin_menu'
            menu = MENU_TREE['admin_menu']
            await send_message(update, context, menu['message'], menu['options'])
            return

        if user_state == 'admin_menu' and user_choice == 'Модерация':
            reviews = context.application.bot_data.get('reviews', [])
            pending_reviews = [review for review in reviews if not review.get('approved', False)]

            if not pending_reviews:
                await send_message(update, context, "Нет отзывов для модерации.",
                                   MENU_TREE['admin_menu']['options'])
                context.user_data['state'] = 'admin_menu'
                return

    # Обработка перехода в калькулятор внутри меню тарифа
    if user_state.startswith('detail_') and user_choice == 'Калькулятор🧮':
        tariff_name = user_state.split('_')[1]
        context.user_data['selected_tariff'] = tariff_name

        if tariff_name == 'Мытье окон🧴':
            context.user_data['state'] = 'enter_window_panels'
            await send_message(update, context, "Введите количество оконных створок:", ['Главное меню🔙'])
        else:
            context.user_data['price_per_sqm'] = CLEANING_PRICES[tariff_name]
            context.user_data['state'] = 'enter_square_meters'
            await send_message(update, context, MENU_TREE['enter_square_meters']['message'],
                               MENU_TREE['enter_square_meters']['options'])
        return

    # Основная логика обработки
    menu = MENU_TREE.get(user_state)
    if user_choice in menu['next_state']:
        next_state = menu['next_state'][user_choice]
        context.user_data['state'] = next_state

        next_menu = MENU_TREE.get(next_state)
        if next_menu:
            await send_message(update, context, next_menu['message'], next_menu['options'])
    else:
        await send_message(update, context, menu.get('fallback', 'Пожалуйста, выберите опцию из меню.'),
                           menu['options'])



async def moderate_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE, user_state: str) -> None:
    pending_reviews = [review for review in context.application.bot_data.get('reviews', [])
                       if not review.get('approved', False) and not review.get('deleted', False)]

    if not pending_reviews:
        await send_message(update, context, "Нет отзывов для модерации.", MENU_TREE['admin_menu']['options'])
        context.user_data['state'] = 'admin_menu'
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

    context.user_data['state'] = 'moderation_menu'



async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем данные пользователя
    user = query.from_user
    user_id = user.id
    username = user.username or "Anonymous"
    user_state = context.user_data.get('state', 'main_menu')

    # Логика обработки нажатий
    if query.data == "show_phone_number":
        await query.message.reply_text("Ваш номер телефона: +79956124581")
        return

    if user_state == 'moderation_menu':
        action, message_id = query.data.split('_')
        pending_reviews = context.application.bot_data.get('reviews', [])
        review = next((r for r in pending_reviews if str(r['message_id']) == message_id), None)

        if review:
            if action == 'delete':
                review['deleted'] = True
                await query.edit_message_text(text="Отзыв безвозвратно удален.")
                context.application.bot_data['reviews'].remove(review)

            elif action == 'publish':
                review['approved'] = True
                await publish_review(context, review)
                await query.edit_message_text(text="Отзыв успешно опубликован.")
                for r in context.application.bot_data['reviews']:
                    if r['user_id'] == review['user_id'] and r['message_id'] == review['message_id']:
                        r['approved'] = True

                # Трекинг отправленного отзыва
                await track_event(
                    user_id=review['user_id'],  # ID отправителя отзыва
                    username=review['user_name'],  # Юзернейм отправителя
                    state='review_published',  # Состояние, связанное с публикацией отзыва
                    is_new=False  # Отзыв уже был отправлен ранее
                )

        # Проверяем, остались ли необработанные отзывы
        remaining_reviews = [r for r in pending_reviews if not r.get('approved', False) and not r.get('deleted', False)]
        if not remaining_reviews:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Все отзывы обработаны.")
            context.user_data.pop('pending_reviews', None)
            context.user_data['state'] = 'admin_menu'
            return

        context.user_data['state'] = 'moderation_menu'




async def show_useful_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # URL для перехода в канал
    channel_url = "https://t.me/+7YI7c3pWXhQwMTcy"

    # Инлайн-кнопка для перехода в канал
    inline_buttons = [[InlineKeyboardButton("Перейти в канал", url=channel_url)]]
    inline_reply_markup = InlineKeyboardMarkup(inline_buttons)

    # Кнопка "Главное меню"
    main_menu_keyboard = [["Главное меню"]]
    reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

    # Отправка сообщения с инлайн-кнопкой
    await update.message.reply_text(
        "Посетите наш канал для получения последних новостей, акций и розыгрышей!",
        reply_markup=inline_reply_markup
    )

    # Отправка сообщения с обычной клавиатурой
    await update.message.reply_text(
        "Выберите действие:",
        reply_markup=reply_markup
    )

# Функция обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = user.id
    username = user.username or "Anonymous"

    # Проверяем, является ли пользователь новым
    is_new = not await check_user_in_database(user_id)

    # Логируем событие "start"
    await track_event(
        user_id=user_id,
        username=username,
        state="start_command",
        is_new=is_new
    )

    # Определяем меню и состояние
    if user_id == ADMIN_ID:
        context.user_data["state"] = "admin_menu"
        menu = MENU_TREE["admin_menu"]
    else:
        context.user_data["state"] = "main_menu"
        menu = MENU_TREE["main_menu"]

    await send_message(update, context, menu["message"], menu["options"])


async def publish_review(context: ContextTypes.DEFAULT_TYPE, review: dict) -> None:
    try:
        if review['photo_file_ids']:
            if len(review['photo_file_ids']) > 1:
                media_group = [InputMediaPhoto(photo_id) for photo_id in review['photo_file_ids']]
                await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
            else:
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=review['photo_file_ids'][0])

        await context.bot.forward_message(
            chat_id=CHANNEL_ID,
            from_chat_id=review['user_id'],
            message_id=review['message_id']
        )

        review['approved'] = True
        logger.info(f"Отзыв от {review['user_name']} успешно опубликован в канал.")
    except Exception as e:
        logger.error(f"Ошибка при публикации отзыва: {e}")
        await context.bot.send_message(chat_id=ADMIN_ID,
                                       text=f"Не удалось опубликовать отзыв от {review['user_name']}. Ошибка: {e}")
