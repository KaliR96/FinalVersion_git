from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from menu_tree import MENU_TREE
from constants import CLEANING_PRICES, CLEANING_DETAILS, CHANNEL_ID
from utils import send_message
from constants import CHANNEL_LINK, ADMIN_ID
from telegram import InputMediaPhoto

import logging

logger = logging.getLogger(__name__)

# Динамическое добавление состояний для каждого тарифа с кнопкой "Калькулятор🧮"
for tariff_name, details in CLEANING_DETAILS.items():
    MENU_TREE[f'detail_{tariff_name}'] = {
        'message': details['details_text'],
        'image_path': details['image_path'],
        'options': ['Калькулятор🧮', 'Назад'],
        'next_state': {
            'Калькулятор🧮': 'calculator_menu',
            'Назад': 'show_tariffs'
        }
    }


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Проверка, является ли запрос текстовым сообщением или callback-запросом
    if update.message:
        # Это текстовое сообщение
        user_message = update.message.text.strip()
        user_state = context.user_data.get('state', 'main_menu')

        logger.info(f"User state: {user_state}, User message: {user_message}")

        # Глобальная обработка кнопки "Связаться📞" независимо от состояния
        if user_message == 'Связаться📞':
            # Инлайн-кнопки для контактов
            keyboard = [
                [InlineKeyboardButton("WhatsApp", url="https://wa.me/79956124581")],
                [InlineKeyboardButton("Telegram", url="https://t.me/kaliroom")],
                [InlineKeyboardButton("Показать номер", callback_data="show_phone_number")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Связаться📞 со мной вы можете через следующие каналы:",
                                            reply_markup=reply_markup)
            context.user_data['state'] = 'contact'
            return  # Прерываем дальнейшую обработку после отправки сообщения

        # Замена Inline-кнопок на вызов функции с Reply-кнопками для "Отзывы💬"
        elif user_message == 'Отзывы💬':
            # Вызываем функцию, которая обрабатывает меню отзывов с Reply-кнопками
            await handle_reviews_menu(update, context)
            return

            # Обработка кнопки "Написать отзыв"
        elif user_state == 'reviews_menu' and user_message == 'Написать отзыв':
            await handle_write_review(update, context)
            return

        # Обработка кнопки "Посмотреть отзывы"
        elif user_state == 'reviews_menu' and user_message == 'Просмотреть отзывы':
            await handle_view_reviews(update, context)
            return

        # Обработка состояния написания отзыва
        elif user_state == 'writing_review':
            await handle_write_review_content(update, context, user_message)
            return


        # Глобальная обработка кнопки "Главное меню🔙"
        elif user_message == 'Главное меню🔙':
            context.user_data['state'] = 'main_menu'
            await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])
            return

        # Глобальная обработка кнопки "Калькулятор🧮"
        elif user_message == 'Калькулятор🧮':
            context.user_data['state'] = 'calculator_menu'
            await send_message(update, context, MENU_TREE['calculator_menu']['message'],
                               MENU_TREE['calculator_menu']['options'])
            return

        # Остальные состояния обрабатываются как обычно
        if user_state == 'main_menu' and user_message == 'Тарифы🏷️':
            context.user_data['state'] = 'show_tariffs'
            await send_message(update, context, "Выберите тариф для получения подробной информации:",
                               MENU_TREE['show_tariffs']['options'])
        elif user_state == 'show_tariffs':
            await handle_show_tariffs(update, context, user_message)
        elif user_state.startswith('detail_') and user_message == 'Калькулятор🧮':
            context.user_data['state'] = 'calculator_menu'
            await send_message(update, context, MENU_TREE['calculator_menu']['message'],
                               MENU_TREE['calculator_menu']['options'])
        elif user_state == 'calculator_menu':
            # Обработка выбора тарифа внутри калькулятора
            if user_message in CLEANING_PRICES:
                context.user_data['selected_tariff'] = user_message
                context.user_data['state'] = 'enter_square_meters'
                await send_message(update, context, "Введите количество квадратных метров для уборки:",
                                   MENU_TREE['enter_square_meters']['options'])
            else:
                await send_message(update, context, "Пожалуйста, выберите тариф из списка:",
                                   MENU_TREE['calculator_menu']['options'])
        elif user_state == 'enter_square_meters':
            await handle_enter_square_meters(update, context, user_message)
        elif user_state == 'enter_window_panels':
            await handle_enter_window_panels(update, context, user_message)
        elif user_state == 'add_extras':
            await handle_add_extras(update, context, user_message)
        else:
            logger.warning(f"Unknown state: {user_state}, redirecting to handle_unknown_message.")
            await handle_unknown_message(update, context)

    elif update.callback_query:
        # Это callback-запрос (нажатие инлайн-кнопки)
        query = update.callback_query
        await query.answer()  # Ответ на callback для индикации

        # Обработка callback-запроса для инлайн-кнопки "Показать номер"
        if query.data == 'show_phone_number':
            await query.edit_message_text(text="Вы можете связаться по номеру: +7 (995) 612-45-81")
        elif query.data == 'write_review':
            await query.edit_message_text(text="Пожалуйста, оставьте свой отзыв на нашем канале.")
        else:
            # Возвращение в главное меню при нажатии на инлайн-кнопку
            menu = MENU_TREE.get(context.user_data.get('state'), MENU_TREE['main_menu'])
            await query.edit_message_text(text=menu['message'], reply_markup=InlineKeyboardMarkup(menu['options']))


# Обработка callback для инлайн-кнопки "Показать номер"
async def show_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Ответ на callback для индикации
    # Отправка номера телефона через edit_message_text
    await query.edit_message_text(text="Вы можете связаться по номеру: +7 (995) 612-45-81")


async def handle_show_tariffs(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает выбор тарифа пользователем."""

    # Удаляем пробелы и лишние символы для точного сравнения
    user_choice = user_choice.strip()

    # Проверяем, что выбор пользователя есть в списке тарифов
    if user_choice in CLEANING_PRICES:
        details = CLEANING_DETAILS.get(user_choice)
        if details:
            try:
                with open(details['image_path'], 'rb') as image_file:
                    await update.message.reply_photo(photo=image_file)
            except FileNotFoundError:
                logger.error(f"Изображение не найдено: {details['image_path']}")
                await update.message.reply_text("Изображение для этого тарифа временно недоступно.")

            # Обновляем состояние пользователя
            context.user_data['selected_tariff'] = user_choice
            context.user_data['state'] = f'detail_{user_choice}'

            # Отправляем подробности тарифа
            for part in details['details_text']:
                await update.message.reply_text(part)

            await send_message(update, context, "Выберите дальнейшее действие:",
                               MENU_TREE[f'detail_{user_choice}']['options'])
        else:
            await send_message(update, context, "Пожалуйста, выберите опцию из меню.",
                               MENU_TREE['show_tariffs']['options'])
    else:
        await send_message(update, context, "Неизвестный тариф. Попробуйте снова.",
                           MENU_TREE['show_tariffs']['options'])


async def handle_enter_square_meters(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str) -> None:
    """Обрабатывает ввод данных квадратных метров."""
    try:
        square_meters = float(user_input)
        context.user_data['square_meters'] = square_meters

        selected_tariff = context.user_data.get('selected_tariff', None)

        if selected_tariff in CLEANING_PRICES:
            price_per_meter = CLEANING_PRICES[selected_tariff]
            total_cost = price_per_meter * square_meters
            context.user_data['total_cost'] = total_cost  # Сохраняем начальную стоимость
            await update.message.reply_text(f"Стоимость уборки: {total_cost} руб.")

        # Если тариф "Генеральная уборка" или "Повседневная уборка" — предлагаем доп. услуги и кнопки
        if selected_tariff in ['Ген.Уборка🧼', 'Повседневная🧹']:
            context.user_data['state'] = 'add_extras'
            await send_message(update, context,
                               "Вы можете выбрать дополнительные услуги, связаться со мной или вернуться в главное меню:",
                               [['Глажка белья', 'Стирка белья'],
                                ['Почистить лоток', 'Уход за цветами'],
                                ['Мытье окон(1 створка)🧴'],
                                ['Связаться📞', 'Главное меню🔙']])
        else:
            # Для других тарифов (например, "Послестрой", "Мытье окон") сразу предлагаем кнопки "Связаться" и "Главное меню"

            await send_message(update, context, "Вы можете связаться со мной или вернуться в главное меню.",
                               [['Связаться📞', 'Главное меню🔙']])
            context.user_data['state'] = 'final_decision'

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для квадратных метров.")


async def handle_enter_window_panels(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str) -> None:
    """Обрабатывает ввод данных количества оконных створок."""
    try:
        num_panels = int(user_input)
        context.user_data['window_panels'] = num_panels
        context.user_data['state'] = 'calculate_result'
        await send_message(update, context, MENU_TREE['calculate_result']['message'],
                           MENU_TREE['calculate_result']['options'])
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для оконных створок.")


async def handle_add_extras(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает выбор дополнительных услуг и завершение взаимодействия."""
    # Доп услуги и их стоимость
    EXTRA_SERVICES = {
        'Глажка белья': 600,
        'Стирка белья': 300,
        'Почистить лоток': 300,
        'Уход за цветами': 200,
        'Мытье окон(1 створка)🧴': 350
    }

    if user_choice in EXTRA_SERVICES:
        extra_cost = EXTRA_SERVICES[user_choice]
        total_cost = context.user_data.get('total_cost', 0)  # Получаем текущую сумму
        total_cost += extra_cost
        context.user_data['total_cost'] = total_cost  # Сохраняем обновленную сумму
        await update.message.reply_text(f"Добавлено: {user_choice}. Общая стоимость: {total_cost} руб.")

        # Продолжаем предлагать доп. услуги или завершение расчета
        await send_message(update, context, "Вы можете добавить ещё услуги или завершить расчет:",
                           [['Глажка белья', 'Стирка белья'],
                            ['Почистить лоток', 'Уход за цветами'],
                            ['Мытье окон(1 створка)🧴'],
                            ['Связаться📞', 'Главное меню🔙']])

    elif user_choice == 'Связаться📞' or user_choice == 'Главное меню🔙':
        total_cost = context.user_data.get('total_cost', 0)
        await update.message.reply_text(f"Итоговая стоимость уборки с доп. услугами: {total_cost} руб.")
        # Переход в главное меню или вывод контактов
        if user_choice == 'Связаться📞':
            await send_message(update, context, MENU_TREE['contact']['message'], MENU_TREE['contact']['options'])
            context.user_data['state'] = 'contact'
        elif user_choice == 'Главное меню🔙':
            context.user_data['state'] = 'main_menu'
            await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])

    else:
        await send_message(update, context, "Пожалуйста, выберите услугу из списка или завершите расчет.",
                           [['Глажка белья', 'Стирка белья'],
                            ['Почистить лоток', 'Уход за цветами'],
                            ['Мытье окон(1 створка)🧴'],
                            ['Связаться📞', 'Главное меню🔙']])


async def handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает неизвестные команды и сообщения."""
    await send_message(update, context, "Извините, я не отправлю это сообщение. Попробуйте выбрать опцию СВЯЗАТЬСЯ")


async def handle_reviews_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает меню отзывов с кнопкой 'Главное меню🔙'."""
    # Создаем Reply-кнопки
    keyboard = [['Написать отзыв', 'Просмотреть отзывы'], ['Главное меню🔙']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    # Отправляем сообщение с Reply-кнопками
    await update.message.reply_text("Что вы хотите сделать?", reply_markup=reply_markup)
    context.user_data['state'] = 'reviews_menu'


async def handle_write_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает состояние написания отзыва."""
    await update.message.reply_text("Пожалуйста, напишите ваш отзыв.")
    context.user_data['state'] = 'writing_review'  # Состояние для написания отзыва


async def handle_view_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает состояние просмотра отзывов."""
    channel_url = "https://t.me/CleaningSphere"  # Реальная ссылка на канал с отзывами
    await update.message.reply_text(f"Просмотрите все отзывы на нашем канале: {channel_url}")

    # Переход в главное меню после просмотра отзывов
    reply_keyboard = [['Главное меню🔙']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Вернуться в главное меню:", reply_markup=reply_markup)

    context.user_data['state'] = 'main_menu'


# Функция для обработки отзыва и отправки его в админский чат
async def handle_write_review_content(update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str) -> None:
    """Обрабатывает содержание отзыва и отправляет его на модерацию в админский чат."""

    # Отправляем отзыв в админский канал для модерации
    await context.bot.send_message(chat_id=ADMIN_ID,
                                   text=f"Новый отзыв от {update.message.from_user.first_name}: {user_message}")

    # Подтверждаем пользователю, что отзыв был получен
    await update.message.reply_text("Спасибо за ваш отзыв! Он был отправлен на модерацию.")

    # Возвращаем пользователя в главное меню (обычного пользователя)
    context.user_data['state'] = 'main_menu'
    await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает контактную информацию."""
    if user_choice == 'Главное меню🔙':
        context.user_data['state'] = 'main_menu'
        await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])
    else:
        await send_message(update, context, "Связаться со мной вы можете через следующие каналы.",
                           MENU_TREE['contact']['options'])


async def handle_useful_info(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает полезную информацию и перенаправляет в канал."""

    if user_choice == 'Главное меню🔙':
        # Возврат в главное меню
        context.user_data['state'] = 'main_menu'
        await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])
    else:
        # Отправляем сообщение с приглашением посетить канал и ссылкой
        await send_message(update, context,
                           f"Посетите наш канал для получения последних новостей, акций и розыгрышей!\n\n{CHANNEL_LINK}",
                           MENU_TREE['useful_info']['options'])


# Обработка callback для инлайн-кнопки "Показать номер"
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем текущее состояние пользователя
    user_state = context.user_data.get('state', 'main_menu')

    # Проверяем нажатие на кнопку с номером телефона
    if query.data == "show_phone_number":
        # Отправляем сообщение с номером телефона
        await query.message.reply_text("Ваш номер телефона: +79956124581")
        return

    # Если состояние пользователя в модерации
    if user_state == 'moderation_menu':
        # Ищем действие и message_id в callback_data
        action, message_id = query.data.split('_')
        pending_reviews = context.application.bot_data.get('reviews', [])
        review = next((r for r in pending_reviews if str(r['message_id']) == message_id), None)

        if review:
            if action == 'delete':
                # Отмечаем отзыв как удаленный
                review['deleted'] = True
                await query.edit_message_text(text="Отзыв безвозвратно удален.")
                context.application.bot_data['reviews'].remove(review)

            elif action == 'publish':
                # Отмечаем отзыв как опубликованный
                review['approved'] = True
                await publish_review(context, review)
                await query.edit_message_text(text="Отзыв успешно опубликован.")
                for r in context.application.bot_data['reviews']:
                    if r['user_id'] == review['user_id'] and r['message_id'] == review['message_id']:
                        r['approved'] = True

        # Проверка оставшихся отзывов для модерации
        remaining_reviews = [r for r in pending_reviews if not r.get('approved', False) and not r.get('deleted', False)]
        if not remaining_reviews:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Все отзывы обработаны.")
            context.user_data.pop('pending_reviews', None)
            context.user_data['state'] = 'admin_menu'
            return

        context.user_data['state'] = 'moderation_menu'

async def publish_review(context: ContextTypes.DEFAULT_TYPE, review: dict) -> None:
    try:
        if review.get('photo_file_ids'):
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


