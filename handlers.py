from telegram import Update, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from config import ADMIN_ID, CHANNEL_ID, logger
from data import CLEANING_PRICES, CLEANING_DETAILS
from menu import MENU_TREE
from utils import send_message, send_inline_message, calculate_windows
from analytics import send_event_to_ga


# Пример отправки сообщения с логированием
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_state = context.user_data.get('state', 'main_menu')
    logger.info("Текущее состояние: %s", user_state)
    user_choice = update.message.text.strip() if update.message and update.message.text else None

    # Переход на состояние "Полезная информация📢"
    if user_choice == 'Полезная информация📢':
        context.user_data['state'] = 'useful_info'
        await show_useful_info(update, context)
        return

    if user_state == 'write_review':
        # Сохраняем ID текущего сообщения с текстом и медиа
        review_text = update.message.caption or update.message.text or ""
        message_id = update.message.message_id
        user_name = update.message.from_user.full_name

        if review_text == MENU_TREE['write_review']['options'][0]:
            await send_message(update, context, "Главное меню", MENU_TREE['main_menu']['options'])
            context.user_data['state'] = 'main_menu'
            return
        elif review_text == '':
            # Сохраняем отзыв как единое сообщение
            review_data = {
                'review': review_text,
                'user_name': user_name,
                'user_id': user_id,
                'message_id': message_id,  # Сохраняем полный message_id для пересылки целого сообщения
                'approved': False
            }

            context.application.bot_data.setdefault('reviews', []).append(review_data)
            logger.info("Отправка сообщения с благодарностью пользователю.")

            # await update.message.reply_text("Спасибо за ваш отзыв! Он будет добавлен через некоторое время.")
            # await send_message(update, context, "Спасибо за ваш отзыв! Он будет добавлен через некоторое время.", MENU_TREE['write_review']['options'])
            context.user_data['state'] = 'write_review'
            return
        else:
            # Сохраняем отзыв как единое сообщение
            review_data = {
                'review': review_text,
                'user_name': user_name,
                'user_id': user_id,
                'message_id': message_id,  # Сохраняем полный message_id для пересылки целого сообщения
                'approved': False
            }

            context.application.bot_data.setdefault('reviews', []).append(review_data)
            logger.info("Отправка сообщения с благодарностью пользователю.")

            # await update.message.reply_text("Спасибо за ваш отзыв! Он будет добавлен через некоторое время.")
            await send_message(update, context, "Спасибо за ваш отзыв! Он будет добавлен через некоторое время.",
                               MENU_TREE['write_review']['options'])
            context.user_data['state'] = 'write_review'
            return

    # Обработка нажатия кнопки "Посмотреть Отзывы💬"
    if user_state == 'reviews_menu' and update.message.text and update.message.text.strip() == 'Посмотреть Отзывы💬':
        channel_url = "https://t.me/CleaningSphere"  # Замените на реальную ссылку на канал
        await update.message.reply_text(f"Просмотрите все отзывы на нашем канале: {channel_url}")

        reply_keyboard = [['Главное меню🔙']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Вернуться в главное меню:", reply_markup=reply_markup)

        context.user_data['state'] = 'main_menu'
        return

    # Обработка нажатия кнопки "Назад" при показе тарифов
    if user_state.startswith('detail_') and update.message.text.strip() == 'Назад':
        context.user_data['state'] = 'show_tariffs'
        await send_message(update, context, MENU_TREE['show_tariffs']['message'], MENU_TREE['show_tariffs']['options'])
        return

    if user_id == ADMIN_ID:
        if user_state == 'main_menu':
            context.user_data['state'] = 'admin_menu'
            menu = MENU_TREE['admin_menu']
            await send_message(update, context, menu['message'], menu['options'])
            return

        if user_state == 'admin_menu':
            if update.message.text.strip() == 'Модерация':
                reviews = context.application.bot_data.get('reviews', [])
                pending_reviews = [review for review in reviews if not review.get('approved', False)]

                if not pending_reviews:
                    await send_message(update, context, "Нет отзывов для модерации.",
                                       MENU_TREE['admin_menu']['options'])
                    context.user_data['state'] = 'admin_menu'
                    return

        elif user_state == 'moderation_menu':
            if update.message.text.strip() == 'Админ меню':
                context.user_data['state'] = 'admin_menu'
                menu = MENU_TREE['admin_menu']
                await send_message(update, context, menu['message'], menu['options'])
                return

    # Обработка модерации отзывов
    if user_id == ADMIN_ID and user_state == 'admin_menu':
        if update.message.text.strip() == 'Модерация':
            await moderate_reviews(update, context, user_state)
            return

    # Обработка состояния "Отзывы💬"
    if user_state == 'reviews_menu':
        if update.message.text.strip() in MENU_TREE['reviews_menu']['next_state']:
            context.user_data['state'] = MENU_TREE['reviews_menu']['next_state'][update.message.text.strip()]
            next_menu = MENU_TREE.get(context.user_data['state'])
            await send_message(update, context, next_menu['message'], next_menu['options'])
        else:
            await send_message(update, context, "Пожалуйста, выберите опцию из меню.",
                               MENU_TREE['reviews_menu']['options'])
        return

    # Если пользователь не администратор, обрабатываем обычные состояния
    menu = MENU_TREE.get(user_state)
    user_choice = update.message.text.strip() if update.message.text else None

    if user_choice == 'Главное меню🔙':
        context.user_data['state'] = 'main_menu'
        menu = MENU_TREE['main_menu']
        await send_message(update, context, menu['message'], menu['options'])
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

    # Обработка выбора тарифа в меню "Тарифы🏷️"
    if user_state == 'show_tariffs' and user_choice in CLEANING_PRICES:
        details = CLEANING_DETAILS.get(user_choice)
        if details:
            try:
                with open(details['image_path'], 'rb') as image_file:
                    await update.message.reply_photo(photo=image_file)
            except FileNotFoundError:
                logger.error(f"Изображение не найдено: {details['image_path']}")
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
    # Обработка ввода квадратных метров
    if user_state == 'enter_square_meters':
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
                # Если выбран тариф без допуслуг (например, "Мытье окон" или "Послестрой"), завершаем расчет
                await send_message(update, context,
                                   "Расчет завершен. Вы можете заказать услугу нажав кнопку 'Связаться📞' !",
                                   MENU_TREE['calculate_result']['options'])
                context.user_data['state'] = 'main_menu'

            # Логирование состояния после отправки сообщения
            logger.info(f"Состояние после отправки сообщения: {context.user_data['state']}")

            return  # Завершаем выполнение функции

        except ValueError:
            # Логируем некорректный ввод и возвращаем пользователя к повторному вводу
            logger.error(f"Некорректное количество квадратных метров: {user_choice}")
            await send_message(update, context, 'Пожалуйста, введите корректное количество квадратных метров.',
                               MENU_TREE['enter_square_meters']['options'])

    # Обработка выбора дополнительных услуг
    if user_state == 'add_extras':
        if user_choice in ['Глажка белья', 'Стирка белья', 'Почистить лоток', 'Уход за цветами', 'Мытье окон🧴(1 створка)']:
            # Добавляем стоимость за выбранную допуслугу
            if user_choice == 'Глажка белья':
                context.user_data['total_cost'] += 300  # Например, 300 руб за глажку
            elif user_choice == 'Стирка белья':
                context.user_data['total_cost'] += 250  # Например, 250 руб за стирку
            elif user_choice == 'Почистить лоток':
                context.user_data['total_cost'] += 150  # Например, 150 руб за чистку лотка
            elif user_choice == 'Уход за цветами':
                context.user_data['total_cost'] += 200  # Например, 200 руб за уход за цветами
            elif user_choice == 'Мытье окон🧴(1 створка)':
                context.user_data['total_cost'] += 350  # Например, 350 руб за одну створку окна

            # Сохраняем выбранные дополнительные услуги в user_data
            context.user_data.setdefault('selected_extras', []).append(user_choice)

            # Логируем текущее состояние для отладки
            logger.info(f"Текущее состояние перед отправкой сообщения: {context.user_data['state']}")

            # Продолжаем выбор допуслуг, всегда показываем кнопку "Главное меню🔙"
            await send_message(update, context,
                               f"Услуга {user_choice} добавлена. Общая стоимость: {context.user_data['total_cost']} руб.\nВыберите еще услуги или свяжитесь с нами.",
                               [['Глажка белья', 'Стирка белья'],
                                ['Почистить лоток', 'Уход за цветами'],
                                ['Мытье окон🧴(1 створка)'],
                                ['Главное меню🔙', 'Связаться📞']])  # Кнопка "Главное меню🔙" всегда включена

            # Остаемся в состоянии add_extras, чтобы пользователь мог выбрать другие услуги
            # После выбора услуги
            context.user_data['state'] = 'add_extras'
            logger.info(f"Состояние изменено на: {context.user_data['state']}")

            # Завершаем выполнение функции, чтобы избежать лишних действий и смены состояния
            return


        # Если пользователь выбрал "Связаться📞", завершаем расчет и переходим к контактам
        elif user_choice == 'Связаться📞':
            # Рассчитываем общую стоимость
            total_cost = context.user_data['total_cost']
            selected_extras = ", ".join(context.user_data.get('selected_extras', []))

            # Отправляем итоговую стоимость с выбранными допуслугами
            final_message = f"Итоговая стоимость уборки: {total_cost:.2f} руб."
            if selected_extras:
                final_message += f"\nВы выбрали следующие дополнительные услуги: {selected_extras}"

            # Отправляем сообщение с результатом
            await send_message(update, context, final_message, MENU_TREE['calculate_result']['options'])

            # Переход в состояние "Связаться"
            context.user_data['state'] = 'contact'
            buttons = [
                [InlineKeyboardButton("WhatsApp", url="https://wa.me/79956124581")],
                [InlineKeyboardButton("Telegram", url="https://t.me/m/xpCumFdPYTBi")],
                [InlineKeyboardButton("Показать номер", callback_data="show_phone_number")]
            ]
            await send_inline_message(update, context, MENU_TREE['contact']['message'], buttons)


        # Если пользователь выбрал "В начало", то сбрасываем процесс и возвращаемся в главное меню
        elif user_choice == 'Главное меню🔙':
            # Рассчитываем общую стоимость
            total_cost = context.user_data['total_cost']
            selected_extras = ", ".join(context.user_data.get('selected_extras', []))

            # Отправляем сообщение с результатом
            final_message = f"Итоговая стоимость уборки: {total_cost:.2f} руб."
            if selected_extras:
                final_message += f"\nВы выбрали следующие дополнительные услуги: {selected_extras}"

            await send_message(update, context, final_message, MENU_TREE['calculate_result']['options'])

            # Переход в главное меню
            context.user_data['state'] = 'main_menu'
            await send_message(update, context, MENU_TREE['main_menu']['message'], MENU_TREE['main_menu']['options'])

        # Сбрасываем список дополнительных услуг, когда расчет закончен
        context.user_data.pop('selected_extras', None)

    # Обработка ввода количества оконных створок для тарифа "мытье окон"
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

    if user_choice in menu['next_state']:
        next_state = menu['next_state'][user_choice]
        context.user_data['state'] = next_state

        if next_state == 'enter_square_meters':
            context.user_data['selected_tariff'] = user_choice  # Запоминаем выбранный тариф
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

    send_event_to_ga(
        user_id=update.effective_user.id,  # Уникальный идентификатор пользователя
        category='User',  # Категория события
        action='ButtonClick',  # Действие
        label=f'Button: {query.data}',  # Описание кнопки
        username=update.effective_user.username  # Опционально передаём юзернейм
    )

    #await query.edit_message_text(text=f"Вы нажали: {query.data}")

    user_state = context.user_data.get('state', 'main_menu')

    if query.data == "show_phone_number":
        await query.message.reply_text("Звоните по номеру: +79956124581")
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
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Отправляем данные в Google Analytics
    send_event_to_ga(
        user_id=user_id,  # Уникальный ID пользователя
        category='User',  # Категория события
        action='Start',  # Действие события
        label=f'User: {username}, ID: {user_id}',  # Описание события
        username=username  # Передаём юзернейм
    )

    if user_id == ADMIN_ID:
        context.user_data['state'] = 'admin_menu'
        menu = MENU_TREE['admin_menu']
    else:
        context.user_data['state'] = 'main_menu'
        menu = MENU_TREE['main_menu']
    await send_message(update, context, menu['message'], menu['options'])


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
