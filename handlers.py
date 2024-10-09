from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from menu_tree import MENU_TREE
from constants import CLEANING_PRICES, CLEANING_DETAILS
from utils import send_message
from constants import CHANNEL_LINK
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


import logging

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.strip()  # Удаляем лишние символы
    user_state = context.user_data.get('state', 'main_menu')

    logger.info(f"User state: {user_state}, User message: {user_message}")

    # Проверка состояния и вызов соответствующей функции
    if user_state == 'main_menu' and user_message == 'Тарифы🏷️':
        context.user_data['state'] = 'show_tariffs'
        await send_message(update, context, "Выберите тариф для получения подробной информации:", MENU_TREE['show_tariffs']['options'])
    elif user_state == 'show_tariffs':
        await handle_show_tariffs(update, context, user_message)
    elif user_state.startswith('detail_') and user_message == 'Калькулятор🧮':
        # Логика обработки нажатия на "Калькулятор🧮"
        context.user_data['state'] = 'calculator_menu'
        await send_message(update, context, MENU_TREE['calculator_menu']['message'], MENU_TREE['calculator_menu']['options'])
    elif user_state == 'calculator_menu':
        # Обработка выбора тарифа внутри калькулятора
        if user_message in CLEANING_PRICES:
            context.user_data['selected_tariff'] = user_message
            context.user_data['state'] = 'enter_square_meters'
            await send_message(update, context, "Введите количество квадратных метров для уборки:", MENU_TREE['enter_square_meters']['options'])
        else:
            await send_message(update, context, "Пожалуйста, выберите тариф из списка:", MENU_TREE['calculator_menu']['options'])
    elif user_state == 'enter_square_meters':
        await handle_enter_square_meters(update, context, user_message)
    elif user_state == 'enter_window_panels':
        await handle_enter_window_panels(update, context, user_message)
    elif user_state == 'add_extras':
        await handle_add_extras(update, context, user_message)
    else:
        logger.warning(f"Unknown state: {user_state}, redirecting to handle_unknown_message.")
        await handle_unknown_message(update, context)


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

        # Проверяем, выбран ли один из тарифов: Генеральная уборка или Повседневная уборка
        if selected_tariff in ['Ген.Уборка🧼', 'Повседневная🧹']:
            context.user_data['state'] = 'add_extras'
            await send_message(update, context, MENU_TREE['add_extras']['message'], MENU_TREE['add_extras']['options'])
        else:
            # Если тариф другой, завершаем расчет
            await update.message.reply_text(f"Итоговая стоимость уборки: {total_cost} руб.")
            context.user_data['state'] = 'main_menu'
            await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для квадратных метров.")


async def handle_enter_window_panels(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str) -> None:
    """Обрабатывает ввод данных количества оконных створок."""
    try:
        num_panels = int(user_input)
        context.user_data['window_panels'] = num_panels
        context.user_data['state'] = 'calculate_result'
        await send_message(update, context, MENU_TREE['calculate_result']['message'], MENU_TREE['calculate_result']['options'])
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для оконных створок.")


async def handle_add_extras(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает выбор дополнительных услуг."""
    # Доп услуги и их стоимость
    EXTRA_SERVICES = {
        'Глажка белья': 600,
        'Стирка белья': 300,
        'Почистить лоток': 300,
        'Уход за цветами': 200,
        'Мытье окон(1 створка)🧴': 350
    }

    # Если пользователь выбрал услугу, прибавляем её стоимость
    if user_choice in EXTRA_SERVICES:
        extra_cost = EXTRA_SERVICES[user_choice]
        total_cost = context.user_data.get('total_cost', 0)  # Получаем текущую сумму
        total_cost += extra_cost
        context.user_data['total_cost'] = total_cost  # Сохраняем обновленную сумму
        await update.message.reply_text(f"Добавлено: {user_choice}. Общая стоимость: {total_cost} руб.")

        # Продолжаем предлагать другие доп услуги
        await send_message(update, context, "Выберите дополнительные услуги или завершите расчет:",
                           MENU_TREE['add_extras']['options'])

    # Если пользователь выбрал "Связаться" или "Главное меню", выводим итоговую сумму
    elif user_choice == 'Связаться📞' or user_choice == 'Главное меню🔙':
        total_cost = context.user_data.get('total_cost', 0)
        await update.message.reply_text(f"Итоговая стоимость уборки: {total_cost} руб.")
        context.user_data['state'] = 'main_menu'  # Возвращаемся в главное меню
        await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])

    # Если пользователь выбрал некорректную опцию
    else:
        await send_message(update, context, "Пожалуйста, выберите услугу из списка.",
                           MENU_TREE['add_extras']['options'])


async def handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает неизвестные команды и сообщения."""
    await send_message(update, context, "Извините, я не отправлю это сообщение. Попробуйте выбрать опцию СВЯЗАТЬСЯ")

async def handle_reviews_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает работу с отзывами."""
    if user_choice in MENU_TREE['reviews_menu']['next_state']:
        next_state = MENU_TREE['reviews_menu']['next_state'][user_choice]
        context.user_data['state'] = next_state
        await send_message(update, context, MENU_TREE[next_state]['message'], MENU_TREE[next_state]['options'])
    else:
        await send_message(update, context, "Выберите опцию для работы с отзывами.", MENU_TREE['reviews_menu']['options'])

async def handle_write_review(update: Update, context: ContextTypes.DEFAULT_TYPE, user_input: str) -> None:
    """Обрабатывает написание отзыва."""
    # Логика для сохранения отзыва
    await update.message.reply_text("Спасибо за ваш отзыв!")
    context.user_data['state'] = 'main_menu'
    await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])

async def handle_view_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает просмотр отзывов."""
    if user_choice == 'Перейти к каналу':
        await update.message.reply_text("Вот ссылка на наш канал: https://t.me/your_channel")
    elif user_choice == 'Главное меню🔙':
        context.user_data['state'] = 'main_menu'
        await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])
    else:
        await send_message(update, context, "Выберите действие для работы с отзывами.", MENU_TREE['view_reviews']['options'])

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает контактную информацию."""
    if user_choice == 'Главное меню🔙':
        context.user_data['state'] = 'main_menu'
        await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])
    else:
        await send_message(update, context, "Связаться со мной вы можете через следующие каналы.", MENU_TREE['contact']['options'])

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

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            query = update.callback_query
            await query.answer()

            user_state = context.user_data.get('state', 'main_menu')

            if user_state in MENU_TREE:
                next_state = MENU_TREE[user_state]['next_state'].get(query.data, user_state)
                context.user_data['state'] = next_state

                menu = MENU_TREE[next_state]
                await send_message(update, context, menu['message'], menu['options'])
            else:
                await send_message(update, context, "Неизвестная команда. Попробуйте снова.")

