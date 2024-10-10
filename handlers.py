from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from menu_tree import MENU_TREE
from constants import CLEANING_PRICES, CLEANING_DETAILS, CHANNEL_ID
from utils import send_message, send_inline_menu
from constants import CHANNEL_LINK, ADMIN_ID
from telegram import InputMediaPhoto
from admin import moderate_reviews, save_review_to_bot_data

import logging

logger = logging.getLogger(__name__)
#aWWE
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
        user_id = update.message.from_user.id
        user_name = update.message.from_user.username or update.message.from_user.first_name
        message_id = update.message.message_id
        user_message = update.message.text.strip()
        user_state = context.user_data.get('state', 'main_menu')

        logger.info(f"User state: {user_state}, User message: {user_message}")

        # Проверка, админ ли пользователь
        if user_id == ADMIN_ID:
            if user_message == 'Модерация':
                await moderate_reviews(update, context)
            elif user_message == 'Админ меню':
                context.user_data['state'] = 'admin_menu'
                await send_message(update, context, MENU_TREE['admin_menu']['message'],
                                   MENU_TREE['admin_menu']['options'])
            elif user_message == 'Назад' and user_state == 'moderation_menu':
                # Возвращаем администратора в админ меню из модерации
                context.user_data['state'] = 'admin_menu'
                await send_message(update, context, MENU_TREE['admin_menu']['message'], MENU_TREE['admin_menu']['options'])
            else:
                await send_message(update, context, "Неизвестная команда для админа.", [["Назад"]])
            return

        # Обработка кнопки "Назад" в состоянии модерации
        if user_message == 'Назад' and user_state == 'moderation_menu':
            context.user_data['state'] = 'admin_menu'
            await send_message(update, context, MENU_TREE['admin_menu']['message'], MENU_TREE['admin_menu']['options'])
            return

        # Обработка меню отзывов
        if user_state == 'reviews_menu' and user_message == 'Написать отзыв':
            # Переводим пользователя в состояние написания отзыва
            context.user_data['state'] = 'writing_review'
            await send_message(update, context, "Пожалуйста, напишите ваш отзыв💬:")
            return

        # Обработка состояния написания отзыва
        if user_state == 'writing_review':
            review_text = user_message  # Текст отзыва - это сообщение пользователя
            review_data = {
                'user_id': user_id,
                'user_name': user_name,
                'message_id': message_id,
                'review': review_text,
                'approved': False,
                'deleted': False
            }
            # Сохраняем отзыв с полным набором аргументов
            await save_review_to_bot_data(context, user_id, user_name, message_id, review_text)
            await send_message(update, context, "Ваш отзыв отправлен на модерацию. Спасибо!")
            context.user_data['state'] = 'main_menu'  # Возвращаем пользователя в главное меню
            return

        # Глобальная обработка кнопки "Связаться📞" независимо от состояния
        if user_message == 'Связаться📞':
            keyboard = [
                [InlineKeyboardButton("WhatsApp", url="https://wa.me/79956124581")],
                [InlineKeyboardButton("Telegram", url="https://t.me/kaliroom")],
                [InlineKeyboardButton("Показать номер", callback_data="show_phone_number")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Связаться📞 со мной вы можете через следующие каналы:", reply_markup=reply_markup)
            context.user_data['state'] = 'contact'
            return

        # Замена Inline-кнопок на вызов функции с Reply-кнопками для "Отзывы💬"
        elif user_message == 'Отзывы💬':
            await handle_reviews_menu(update, context)
            return

        # Глобальная обработка кнопки "Главное меню🔙"
        elif user_message == 'Главное меню🔙':
            context.user_data['state'] = 'main_menu'
            await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])
            return

        # Глобальная обработка кнопки "Калькулятор🧮"
        elif user_message == 'Калькулятор🧮':
            context.user_data['state'] = 'calculator_menu'
            await send_message(update, context, MENU_TREE['calculator_menu']['message'], MENU_TREE['calculator_menu']['options'])
            return

    elif update.callback_query:
        query = update.callback_query
        await query.answer()  # Ответ на callback для индикации

        # Обработка callback-запроса для инлайн-кнопки "Показать номер"
        if query.data == 'show_phone_number':
            await query.edit_message_text(text="Вы можете связаться по номеру: +7 (995) 612-45-81")
        elif query.data == 'write_review':
            await query.edit_message_text(text="Пожалуйста, оставьте свой отзыв на нашем канале.")
        else:
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


async def handle_view_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает состояние просмотра отзывов."""
    channel_url = "https://t.me/CleaningSphere"  # Реальная ссылка на канал с отзывами
    await update.message.reply_text(f"Просмотрите все отзывы на нашем канале: {channel_url}")

    # Переход в главное меню после просмотра отзывов
    reply_keyboard = [['Главное меню🔙']]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Вернуться в главное меню:", reply_markup=reply_markup)

    context.user_data['state'] = 'main_menu'

async def handle_write_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает состояние написания отзыва."""
    await update.message.reply_text("Пожалуйста, напишите ваш отзыв.")
    context.user_data['state'] = 'writing_review'  # Состояние для написания отзыва

# Функция для обработки отзыва и отправки его в админский чат
async def handle_write_review_content(update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str) -> None:
    """Обрабатывает контент отзыва, отправленный пользователем."""
    review = {
        'user_id': update.message.from_user.id,
        'user_name': update.message.from_user.first_name,
        'message_id': update.message.message_id,
        'text': user_message,
        'approved': False,
        'deleted': False,
        'photo_file_ids': []  # Если у нас будут фото, можно будет их добавить сюда
    }

    # Сохраняем отзыв в bot_data для модерации
    if 'reviews' not in context.application.bot_data:
        context.application.bot_data['reviews'] = []

    context.application.bot_data['reviews'].append(review)

    await update.message.reply_text("Ваш отзыв отправлен на модерацию. Спасибо!")

    # Переводим пользователя обратно в главное меню
    context.user_data['state'] = 'main_menu'
    await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])

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
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"Ошибка при публикации отзыва: {e}")

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
async def button_click(update, context):
    query = update.callback_query
    query_data = query.data
    user_state = context.user_data.get('state', 'main_menu')

    # Обработка кнопки "Назад" в состоянии модерации
    if user_state == 'moderation_menu' and query_data == 'Назад':
        context.user_data['state'] = 'admin_menu'
        await send_inline_menu(update, context, MENU_TREE['admin_menu']['message'], MENU_TREE['admin_menu']['options'])

    else:
        await query.answer("Неизвестная команда для админа.")




