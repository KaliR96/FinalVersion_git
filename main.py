from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import TOKEN, logger
from handlers import start, handle_message, button_click
from analytics import send_event_to_ga


def main():
    logger.info("Запуск бота")
    send_event_to_ga('Bot', 'Start', 'Bot started')
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_click))
    logger.info("Бот успешно запущен, начало polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
