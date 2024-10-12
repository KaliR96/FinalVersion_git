# handlers.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from config import ADMIN_ID, CHANNEL_ID, logger, CLEANING_PRICES
from menu import MENU_TREE
from data import CLEANING_DETAILS
from utils import send_message, send_inline_message, get_image_path, get_description
from calculator import calculate, calculate_windows

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_state = context.user_data.get('state', 'main_menu')
    logger.info(f"Текущее состояние: {user_state}")
    user_choice = update.message.text.strip() if update.message.text else None

    # Обработка команды /start
    if user_choice == '/start':
        await start(update, context)
        return

    # Обработка состояния "Полезная информация📢"
    if user_choice == 'Полезная информация📢':
        context.user_data['state'] = 'useful_info'
        await show_useful_info(update, context)
        return

    # Обработка остальных состояний
    menu = MENU_TREE.get(user_state)
    if not menu:
        context.user_data['state'] = 'main_menu'
        menu = MENU_TREE['main_menu']
        await send_message(update, context, menu['message'], menu['options'])
        return

    if user_choice == 'Главное меню🔙':
        context.user_data['state'] = 'main_menu'
        menu = MENU_TREE['main_menu']
        await send_message(update, context, menu['message'], menu['options'])
        return

    # Обработка выбора тарифа в меню "Тарифы🏷️"
    if user_state == 'show_tariffs' and user_choice in CLEANING_PRICES:
        details = CLEANING_DETAILS.get(user_choice)
        if details:
            image_path = get_image_path(user_choice)
            try:
                with open(image_path, 'rb') as image_file:
                    await update.message.reply_photo(photo=image_file)
            except FileNotFoundError:
                logger.error(f"Изображение не найдено: {image_path}")
                await update.message.reply_text("Изображение для этого тарифа временно недоступно.")

            context.user_data['selected_tariff'] = user_choice
            context.user_data['state'] = f'detail_{user_choice}'

            for part in details['details_text']:
                await update.message.reply_text(part)

            await send_message(update, context, "Выберите дальнейшее действие:",
                               MENU_TREE[f'detail_{user_choice}']['options'])
        else:
            await send_message(update, context, "Пожалуйста, выберите опцию из меню.",
                               MENU_TREE['show_tariffs']['options'])
        return

    # Обработка выбора тарифа в Калькуляторе🧮
    if user_state == 'calculator_menu' and user_choice in CLEANING_PRICES:
        context.user_data['selected_tariff'] = user_choice
        if user_choice == 'Мытье окон🧴':
            context.user_data['state'] = 'enter_window_panels'
            await send_message(update, context, MENU_TREE['enter_window_panels']['message'],
                               MENU_TREE['enter_window_panels']['options'])
        else:
            context.user_data['price_per_sqm'] = CLEANING_PRICES[user_choice]
            context.user_data['state'] = 'enter_square_meters'
            await send_message(update, context, MENU_TREE['enter_square_meters']['message'],
                               MENU_TREE['enter_square_meters']['options'])
        return

    # Обработка ввода квадратных метров
    if user_state == 'enter_square_meters':
        try:
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

            # Проверка минимальной стоимости
            if total_cost < 1500:
                total_cost = 1500
                result_message = (
                    f'Стоимость вашей уборки: 1500.00 руб.\n'
                    'Это минимальная стоимость заказа.'
                )
            else:
                result_message = f'Стоимость вашей уборки: {total_cost:.2f} руб. за {sqm:.2f} кв.м.'

            # Отправляем результат пользователю
            await send_message(update, context, result_message, MENU_TREE['calculate_result']['options'])

            # Сохраняем площадь и стоимость для дальнейшего использования
            context.user_data['square_meters'] = sqm
            context.user_data['total_cost'] = total_cost

            # Проверяем выбранный тариф и предлагаем допуслуги только для "Ген.Уборка🧼" и "Повседневная🧹"
            selected_tariff = context.user_data.get('selected_tariff')
            if selected_tariff in ['Ген.Уборка🧼', 'Повседневная🧹']:
                # Переходим к предложению дополнительных услуг, задаем кнопки с допуслугами
                extras_options = [
                    ['Глажка белья', 'Стирка белья'],
                    ['Почистить лоток', 'Уход за цветами'],
                    ['Мытье окон🧴(1 створка)'],
                    ['Главное меню🔙', 'Связаться📞']
                ]
                await send_message(update, context, "Хотите добавить дополнительные услуги?", extras_options)
                context.user_data['state'] = 'add_extras'
            else:
                # Если выбран тариф без допуслуг (например, "Послестрой"), завершаем расчет
                await send_message(update, context,
                                   "Расчет завершен. Вы можете заказать услугу нажав кнопку 'Связаться📞' !",
                                   MENU_TREE['calculate_result']['options'])
                context.user_data['state'] = 'main_menu'

            return

        except ValueError:
            logger.error(f"Некорректное количество квадратных метров: {user_choice}")
            await send_message(update, context, 'Пожалуйста, введите корректное количество квадратных метров.',
                               MENU_TREE['enter_square_meters']['options'])
            return

    # Обработка выбора дополнительных услуг
    if user_state == 'add_extras':
        if user_choice in ['Глажка белья', 'Стирка белья', 'Почистить лоток', 'Уход за цветами', 'Мытье окон🧴(1 створка)']:
            # Добавляем стоимость за выбранную допуслугу
            if user_choice == 'Глажка белья':
                context.user_data['total_cost'] += 300
            elif user_choice == 'Стирка белья':
                context.user_data['total_cost'] += 250
            elif user_choice == 'Почистить лоток':
                context.user_data['total_cost'] += 150
            elif user_choice == 'Уход за цветами':
                context.user_data['total_cost'] += 200
            elif user_choice == 'Мытье окон🧴(1 створка)':
                context.user_data['total_cost'] += 350

            # Сохраняем выбранные дополнительные услуги в user_data
            context.user_data.setdefault('selected_extras', []).append(user_choice)

            # Продолжаем выбор допуслуг
            await send_message(update, context,
                               f"Услуга {user_choice} добавлена. Общая стоимость: {context.user_data['total_cost']} руб.\nВыберите еще услуги или свяжитесь с нами.",
                               [['Глажка белья', 'Стирка белья'],
                                ['Почистить лоток', 'Уход за цветами'],
                                ['Мытье окон🧴(1 створка)'],
                                ['Главное меню🔙', 'Связаться📞']])

            context.user_data['state'] = 'add_extras'
            return

        elif user_choice == 'Связаться📞':
            # Рассчитываем общую стоимость
            total_cost = context.user_data['total_cost']
            selected_extras = ", ".join(context.user_data.get('selected_extras', []))

            # Отправляем итоговую стоимость с выбранными допуслугами
            final_message = f"Итоговая стоимость уборки: {total_cost:.2f} руб."
            if selected_extras:
                final_message += f"\nВы выбрали следующие дополнительные услуги: {selected_extras}"

            await send_message(update, context, final_message, MENU_TREE['calculate_result']['options'])

            # Переход в состояние "Связаться"
            context.user_data['state'] = 'contact'
            buttons = [
                [InlineKeyboardButton("WhatsApp", url="https://wa.me/79956124581")],
                [InlineKeyboardButton("Telegram", url="https://t.me/kaliroom")],
                [InlineKeyboardButton("Показать номер", callback_data="show_phone_number")]
            ]
            await send_inline_message(update, context, MENU_TREE['contact']['message'], buttons)

        elif user_choice == 'Главное меню🔙':
            # Рассчитываем общую стоимость
            total_cost = context.user_data['total_cost']
            selected_extras = ", ".join(context.user_data.get('selected_extras', []))

            final_message = f"Итоговая стоимость уборки: {total_cost:.2f} руб."
            if selected_extras:
                final_message += f"\nВы выбрали следующие дополнительные услуги: {selected_extras}"

            await send_message(update, context, final_message, MENU_TREE['calculate_result']['options'])

            # Переход в главное меню
            context.user_data['state'] = 'main_menu'
            await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])

        # Сбрасываем список дополнительных услуг
        context.user_data.pop('selected_extras', None)
        return

    # Обработка ввода количества оконных створок для тарифа "Мытье окон"
    if user_state == 'enter_window_panels':
        try:
            num_panels = int(user_choice)
            price_per_panel = CLEANING_PRICES['Мытье окон🧴']

            result = calculate_windows(price_per_panel, num_panels)

            await send_message(update, context, result['formatted_message'], MENU_TREE['calculate_result']['options'])
            context.user_data['state'] = 'main_menu'
        except ValueError:
            await send_message(update, context, 'Пожалуйста, введите корректное количество оконных створок.',
                               ['Главное меню🔙'])
        return

    # Обработка перехода в меню "Связаться📞"
    if user_state == 'main_menu' and user_choice == 'Связаться📞':
        context.user_data['state'] = 'contact'

        buttons = [
            [InlineKeyboardButton("WhatsApp", url="https://wa.me/79956124581")],
            [InlineKeyboardButton("Telegram", url="https://t.me/kaliroom")],
            [InlineKeyboardButton("Показать номер", callback_data="show_phone_number")]
        ]
        await send_inline_message(update, context, MENU_TREE['contact']['message'], buttons)

        reply_keyboard = [['Главное меню🔙']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=reply_markup)
        return

    # Обработка остальных состояний и действий
    # ...

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_state = context.user_data.get('state', 'main_menu')

    if query.data == "show_phone_number":
        await query.message.reply_text("Наш номер телефона: +79956124581")
        return

    # Обработка модерации отзывов и других inline-кнопок
    # ...

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        context.user_data['state'] = 'admin_menu'
        menu = MENU_TREE['admin_menu']
    else:
        context.user_data['state'] = 'main_menu'
        menu = MENU_TREE['main_menu']

    await send_message(update, context, menu['message'], menu['options'])

async def show_useful_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    channel_url = "https://t.me/your_channel_link"  # Замените на вашу реальную ссылку

    buttons = [[InlineKeyboardButton("Перейти в канал", url=channel_url)]]
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "Посетите наш канал для получения последних новостей, акций и розыгрышей!",
        reply_markup=reply_markup
    )

# Дополнительные функции и обработчики (moderate_reviews, publish_review и т.д.)
# ...

