from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, \
    InlineKeyboardMarkup  # Правильные импорты кнопок
from telegram.ext import ContextTypes
from utils import send_tariff_details  # Импорт функции из utils.py
from menu_tree import MENU_TREE
from constants import CLEANING_PRICES, CLEANING_DETAILS
from utils import send_message, send_inline_message
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
    user_id = update.message.from_user.id
    user_state = context.user_data.get('state', 'main_menu')  # Текущее состояние пользователя или 'main_menu' по умолчанию
    user_choice = update.message.text.strip()  # Текст сообщения от пользователя

    # Логирование текущей информации для отладки
    logger.info(f"User {user_id} in state {user_state} selected: {user_choice}")

    # Главное меню
    if user_state == 'main_menu':
        if user_choice == 'Полезная информация📢':
            # Переход на состояние "Полезная информация"
            context.user_data['state'] = 'useful_info'
            await show_useful_info(update, context)
            return

        elif user_choice == 'Тарифы🏷️':
            # Переход на состояние "Показ тарифов"
            context.user_data['state'] = 'show_tariffs'
            await send_message(update, context, MENU_TREE['show_tariffs']['message'], MENU_TREE['show_tariffs']['options'])
            return

        elif user_choice == 'Отзывы💬':
            # Переход на состояние "Отзывы"
            context.user_data['state'] = 'reviews_menu'
            await send_message(update, context, MENU_TREE['reviews_menu']['message'], MENU_TREE['reviews_menu']['options'])
            return

        elif user_choice == 'Связаться📞':
            # Переход на состояние "Контакты"
            context.user_data['state'] = 'contact_menu'
            await send_message(update, context, MENU_TREE['contact_menu']['message'], MENU_TREE['contact_menu']['options'])
            return

        else:
            # Если не распознано, остаёмся в главном меню
            await send_message(update, context, "Пожалуйста, выберите опцию из меню.", MENU_TREE['main_menu']['options'])
            return

    # Меню тарифов
    elif user_state == 'show_tariffs':
        if user_choice in CLEANING_DETAILS:  # Проверяем, что тариф существует в данных
            # Отправляем детали выбранного тарифа
            await send_tariff_details(update, context, user_choice)
            return

        elif user_choice == 'Назад🔙':
            # Возврат в главное меню
            context.user_data['state'] = 'main_menu'
            await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])
            return

    # Меню отзывов
    elif user_state == 'reviews_menu':
        if user_choice == 'Написать отзыв📝':
            # Переход на состояние написания отзыва
            context.user_data['state'] = 'write_review'
            await send_message(update, context, "Пожалуйста, напишите ваш отзыв:", [['Назад🔙']])
            return

        elif user_choice == 'Назад🔙':
            # Возврат в главное меню
            context.user_data['state'] = 'main_menu'
            await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])
            return

    # Написание отзыва
    elif user_state == 'write_review':
        review_text = update.message.text  # Считываем текст отзыва
        if review_text:
            # Обработка отзыва и возврат в главное меню
            review_data = {'review': review_text, 'user_id': user_id, 'approved': False}
            context.application.bot_data.setdefault('reviews', []).append(review_data)
            await send_message(update, context, "Спасибо за ваш отзыв! Он будет опубликован после модерации.", MENU_TREE['main_menu']['options'])
            context.user_data['state'] = 'main_menu'
            return

    # Калькулятор услуг
    elif user_state == 'calculator_menu':
        if user_choice in CLEANING_PRICES:
            # Переход на состояние ввода квадратных метров
            context.user_data['selected_tariff'] = user_choice
            context.user_data['state'] = 'enter_square_meters'
            await send_message(update, context, "Введите количество квадратных метров:", [['Назад🔙']])
            return

    # Ввод метража для тарифа
    elif user_state == 'enter_square_meters':
        await handle_square_meters_input(update, context)  # Обрабатываем ввод метража
        return

    # Если состояние не распознано, возвращаемся в главное меню
    else:
        logger.warning(f"Неизвестное состояние: {user_state}. Возврат в главное меню.")
        context.user_data['state'] = 'main_menu'
        await send_message(update, context, "Пожалуйста, выберите опцию из меню.", MENU_TREE['main_menu']['options'])



async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query  # Получаем объект нажатой кнопки
    await query.answer()  # Обязательный вызов для завершения запроса

    # Получаем текущее состояние пользователя
    user_state = context.user_data.get('state', 'main_menu')

    # Логируем текущее состояние и данные кнопки
    logger.info(f"User {query.from_user.id} in state {user_state} clicked button with data: {query.data}")

    # Пример: если нажата кнопка с номером телефона
    if query.data == "show_phone_number":
        await query.message.reply_text("Ваш номер телефона: +79956124581")
        return

    # Пример: если пользователь в меню модерации отзывов
    if user_state == 'moderation_menu':
        # Данные callback_data в формате 'action_message_id', например: 'publish_12345' или 'delete_12345'
        action, message_id = query.data.split('_')

        pending_reviews = context.application.bot_data.get('reviews', [])
        review = next((r for r in pending_reviews if str(r['message_id']) == message_id), None)

        if review:
            if action == 'delete':
                # Удаление отзыва
                review['deleted'] = True
                await query.edit_message_text(text="Отзыв был удален.")
                context.application.bot_data['reviews'].remove(review)
                logger.info(f"Review {message_id} deleted by admin {query.from_user.id}.")
            elif action == 'publish':
                # Публикация отзыва
                review['approved'] = True
                await publish_review(context, review)  # Опубликование отзыва
                await query.edit_message_text(text="Отзыв успешно опубликован.")
                logger.info(f"Review {message_id} published by admin {query.from_user.id}.")

        # Проверка оставшихся отзывов для модерации
        remaining_reviews = [r for r in pending_reviews if not r.get('approved', False) and not r.get('deleted', False)]
        if not remaining_reviews:
            await context.bot.send_message(chat_id=query.message.chat_id, text="Все отзывы обработаны.")
            context.user_data['state'] = 'admin_menu'
            return

        return

    # Пример: если пользователь в состоянии "Связаться"
    if user_state == 'contact':
        if query.data == "show_phone_number":
            # Отправка номера телефона
            await query.message.reply_text("Наш контактный телефон: +79956124581")
            return

    # Если кнопка не соответствует текущему состоянию пользователя
    await query.message.reply_text("Пожалуйста, выберите правильную опцию.")


async def show_useful_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Ссылка на ваш Telegram-канал или другую полезную информацию
    channel_url = "https://t.me/your_channel"  # Замените на вашу реальную ссылку

    # Создаем Inline-кнопку с ссылкой на канал
    buttons = [[InlineKeyboardButton("Перейти в наш канал", url=channel_url)]]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Отправляем сообщение с кнопкой
    await update.message.reply_text(
        "Посетите наш Telegram-канал, чтобы получать последние новости, акции и специальные предложения!",
        reply_markup=reply_markup
    )

    # Логируем отправку сообщения для отладки
    logger.info(f"Полезная информация отправлена пользователю {update.message.from_user.id}")


async def handle_square_meters_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text.strip()
    try:
        # Пробуем преобразовать введенные данные в число с плавающей точкой
        sqm = float(user_choice)
        logger.info(f"Введенное количество квадратных метров: {sqm}")

        price_per_sqm = context.user_data.get('price_per_sqm')
        if price_per_sqm is None:
            await send_message(update, context,
                               'Произошла ошибка. Пожалуйста, вернитесь в главное меню и начните заново.',
                               ['Главное меню🔙'])
            context.user_data['state'] = 'main_menu'
            return

        # Считаем итоговую стоимость
        total_cost = price_per_sqm * sqm
        total_cost = max(total_cost, 1500)  # Минимальная стоимость 1500 руб.

        result_message = (
            f'Стоимость вашей уборки: {total_cost:.2f} руб. за {sqm:.2f} кв.м.'
        )
        await send_message(update, context, result_message, MENU_TREE['calculate_result']['options'])

        # Сохраняем площадь и стоимость для дальнейшего использования
        context.user_data['square_meters'] = sqm
        context.user_data['total_cost'] = total_cost

        # Проверяем выбранный тариф и предлагаем допуслуги
        selected_tariff = context.user_data.get('selected_tariff')
        if selected_tariff in ['Ген.Уборка🧼', 'Повседневная🧹']:
            await prompt_for_extras(update, context)
        else:
            await complete_calculation(update, context)

        return  # Завершаем выполнение функции

    except ValueError:
        logger.error(f"Некорректное количество квадратных метров: {user_choice}")
        await send_message(update, context, 'Пожалуйста, введите корректное количество квадратных метров.',
                           MENU_TREE['enter_square_meters']['options'])


async def prompt_for_extras(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Список дополнительных услуг
    extras_options = [
        ['Глажка белья', 'Стирка белья'],
        ['Почистить лоток', 'Уход за цветами'],
        ['Мытье окон🧴(1 створка)'],
        ['Главное меню🔙', 'Связаться📞']
    ]

    # Создание клавиатуры с дополнительными услугами
    reply_markup = ReplyKeyboardMarkup(
        extras_options, resize_keyboard=True, one_time_keyboard=True
    )

    # Сообщение пользователю с предложением выбрать дополнительные услуги
    await update.message.reply_text(
        "Хотите добавить дополнительные услуги?",
        reply_markup=reply_markup
    )

    # Устанавливаем состояние для пользователя, чтобы бот знал, что он выбирает доп. услуги
    context.user_data['state'] = 'add_extras'

    # Логирование для отладки
    logger.info(f"Пользователю {update.message.from_user.id} предложены дополнительные услуги.")


async def moderate_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE, user_state: str) -> None:
    # Получаем список отзывов, которые находятся на модерации
    pending_reviews = context.application.bot_data.get('reviews', [])
    # Отбираем только те отзывы, которые не опубликованы и не удалены
    pending_reviews = [review for review in pending_reviews if
                       not review.get('approved', False) and not review.get('deleted', False)]

    # Проверяем, есть ли отзывы для модерации
    if not pending_reviews:
        await update.message.reply_text("Нет отзывов для модерации.")
        context.user_data['state'] = 'admin_menu'
        return

    # Проходим по каждому отзыву и предлагаем администратору действия (опубликовать/удалить)
    for review in pending_reviews:
        user_name = review.get('user_name', 'Анонимный пользователь')
        review_text = review.get('review', 'Без текста')

        # Формируем сообщение с текстом отзыва
        review_message = f"Отзыв от {user_name}:\n\n{review_text}"

        # Кнопки для модерации: опубликовать или удалить отзыв
        buttons = [
            [InlineKeyboardButton("Опубликовать", callback_data=f"publish_{review['message_id']}")],
            [InlineKeyboardButton("Удалить", callback_data=f"delete_{review['message_id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        # Отправляем сообщение с отзывом и кнопками для действий
        await update.message.reply_text(review_message, reply_markup=reply_markup)

    # Устанавливаем состояние "moderation_menu", чтобы бот знал, что администратор находится в режиме модерации
    context.user_data['state'] = 'moderation_menu'

    # Логирование для отладки
    logger.info(f"Администратор {update.message.from_user.id} просматривает отзывы для модерации.")


async def publish_review(context: ContextTypes.DEFAULT_TYPE, review: dict) -> None:
    # ID канала, куда будут публиковаться отзывы (замените на реальный ID канала)
    review_channel_id = "@your_review_channel"

    # Получаем информацию из отзыва
    user_name = review.get('user_name', 'Анонимный пользователь')
    review_text = review.get('review', 'Без текста')

    # Формируем сообщение для публикации
    review_message = f"<b>Отзыв от {user_name}:</b>\n\n{review_text}"

    # Отправляем сообщение в канал с отзывами (включаем поддержку HTML разметки)
    await context.bot.send_message(
        chat_id=review_channel_id,
        text=review_message,
        parse_mode='HTML'  # Используем HTML для форматирования текста
    )

    # Логируем успешную публикацию
    logger.info(f"Отзыв от {user_name} опубликован в канале {review_channel_id}.")

    # Обновляем статус отзыва как "опубликованный"
    review['approved'] = True


def calculate_windows(price_per_panel: float, num_panels: int) -> dict:
    # Рассчитываем общую стоимость
    total_cost = price_per_panel * num_panels

    # Проверяем минимальную стоимость (например, 1000 руб.)
    minimum_cost = 1000  # Минимальная стоимость услуги
    if total_cost < minimum_cost:
        total_cost = minimum_cost

    # Формируем отформатированное сообщение для пользователя
    formatted_message = (
        f"Вы выбрали мойку {num_panels} оконных створок.\n"
        f"Стоимость за одну створку: {price_per_panel:.2f} руб.\n"
        f"Итоговая стоимость мойки: {total_cost:.2f} руб."
    )

    # Возвращаем результат в виде словаря
    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }


async def complete_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Получаем общую стоимость заказа из данных пользователя
    total_cost = context.user_data.get('total_cost', 0)
    selected_extras = context.user_data.get('selected_extras', [])

    # Формируем сообщение с итоговой стоимостью
    final_message = f"Итоговая стоимость услуг: {total_cost:.2f} руб."

    if selected_extras:
        # Если есть дополнительные услуги, добавляем их в сообщение
        extras_list = ", ".join(selected_extras)
        final_message += f"\nВы выбрали следующие дополнительные услуги: {extras_list}"

    # Отправляем сообщение с итоговой стоимостью
    await update.message.reply_text(final_message)

    # Формируем inline-кнопки для завершения заказа
    buttons = [
        [InlineKeyboardButton("Связаться📞", url="https://t.me/your_contact")],
        [InlineKeyboardButton("WhatsApp", url="https://wa.me/your_number")],
        [InlineKeyboardButton("Показать номер телефона", callback_data="show_phone_number")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Отправляем сообщение с кнопками для связи
    await send_inline_message(update, context, "Чтобы завершить заказ, свяжитесь с нами через Telegram или WhatsApp:",
                              buttons)

    # Логируем завершение расчета
    logger.info(
        f"Расчет завершен для пользователя {update.message.from_user.id} с итоговой стоимостью: {total_cost:.2f} руб.")

    # Сбрасываем состояние пользователя на главное меню
    context.user_data['state'] = 'main_menu'
