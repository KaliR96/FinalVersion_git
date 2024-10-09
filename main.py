import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers import handle_message, button_click  # Обработчики сообщений и кнопок
from utils import send_message  # Импортируем утилиты, если нужно для вызовов
from constants import TOKEN  # Импортируем токен для бота
from menu_tree import MENU_TREE

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Основная функция для запуска бота
async def start(update, context):
    """Обрабатывает команду /start"""
    # Устанавливаем состояние и отправляем стартовое сообщение
    context.user_data['state'] = 'main_menu'
    await send_message(update, context, "Привет! Выберите действие из меню", MENU_TREE['main_menu']['options'])

def main():
    """Функция для инициализации и запуска бота"""
    # Создаем экземпляр приложения бота с токеном
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))  # Обработка команды /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Обработка сообщений
    application.add_handler(CallbackQueryHandler(button_click))  # Обработка нажатий на inline-кнопки

    # Запуск polling
    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()
