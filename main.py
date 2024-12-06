from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import TOKEN, logger
from handlers import start, handle_message, button_click
from analytics import track_event  # Для трекинга событий
from database import init_database  # Для инициализации базы

async def track_start_event():
    # Трекинг запуска бота
    await track_event(
        user_id=0,
        username=None,
        state="start",
        is_new=False
    )

def main():
    logger.info("Запуск бота")
    init_database()  # Инициализация базы данных

    application = Application.builder().token(TOKEN).build()

    # Трек события "запуск бота"
    application.job_queue.run_once(track_start_event, 0)

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_click))

    logger.info("Бот успешно запущен, начало polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
