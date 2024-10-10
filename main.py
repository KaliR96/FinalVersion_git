import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers import show_phone_number, handle_message, button_click  # Обработчики сообщений и кнопок
from utils import send_message  # Импортируем утилиты, если нужно для вызовов
from constants import TOKEN, ADMIN_ID  # Импортируем токен и ID администратора для бота
from menu_tree import MENU_TREE
# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Основная функция для запуска бота
async def start(update, context):
    """Обрабатывает команду /start для пользователя и администратора"""
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        # Если админ, показать админ-меню
        context.user_data['state'] = 'admin_menu'
        await send_message(update, context, MENU_TREE['admin_menu']['message'], MENU_TREE['admin_menu']['options'])
    else:
        # Обычное меню для пользователя
        context.user_data['state'] = 'main_menu'
        await send_message(update, context, 'Привет! Я Вера, твоя фея чистоты.\n\nМой робот-уборщик поможет:\n\n🔍Ознакомиться с моими '
                       'услугами\n\n🧮Рассчитать стоимость уборки\n\n🚗Заказать клининг на дом\n\n📞Связаться со мной.', MENU_TREE['main_menu']['options'])

def main():
    """Функция для инициализации и запуска бота"""
    # Создаем экземпляр приложения бота с токеном
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))  # Обработка команды /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Обработка сообщений
    application.add_handler(CallbackQueryHandler(button_click))  # Обработка нажатий на inline-кнопки

    application.add_handler(CallbackQueryHandler(show_phone_number, pattern='show_phone_number'))

    # Запуск polling
    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()
