
from telegram.ext import CommandHandler, MessageHandler, filters
from views import send_cleaning_options, send_cleaning_details
from models import calculate_cleaning_cost

async def start(update, context):
    # Starting command for the bot
    await update.message.reply_text('Привет! Я помогу вам выбрать услугу по уборке. Выберите нужный тариф.')

async def handle_cleaning_type(update, context):
    # Handle user selection of cleaning type
    service_type = update.message.text
    await send_cleaning_details(update, context, service_type)

async def calculate_cost(update, context):
    # Handle cost calculation for a selected service
    try:
        service_type = context.user_data['selected_service']
        square_meters = int(update.message.text)
        cost = calculate_cleaning_cost(service_type, square_meters)
        if cost:
            await update.message.reply_text(f'Стоимость уборки: {cost} руб.')
        else:
            await update.message.reply_text('Не удалось рассчитать стоимость.')
    except (ValueError, KeyError):
        await update.message.reply_text('Пожалуйста, введите правильные данные.')
