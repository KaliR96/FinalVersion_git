from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from handlers import handle_message, button_click
from telegram import Update
from constants import ADMIN_ID
from utils import send_message
from menu_tree import MENU_TREE
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '7363733923:AAHKPw_fvjG2F3PBE2XP6Sj49u04uy7wpZE'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        context.user_data['state'] = 'admin_menu'
        menu = MENU_TREE['admin_menu']
    else:
        context.user_data['state'] = 'main_menu'
        menu = MENU_TREE['main_menu']

    await send_message(update, context, menu['message'], menu['options'])


def main():
    logger.info("Запуск бота")
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_click))

    logger.info("Бот успешно запущен, начало polling...")
    application.run_polling()


if __name__ == '__main__':
    main()
