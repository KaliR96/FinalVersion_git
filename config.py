# config.py

import os
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ID вашего канала (замените на ваш реальный CHANNEL_ID)
CHANNEL_ID = -1002249882445  # Замените на ваш реальный ID канала

# Укажите ваш Telegram ID (замените на ваш реальный ADMIN_ID)
ADMIN_ID = 1238802718  # Замените на ваш реальный Telegram ID

# Цены на квадратный метр для каждого типа уборки
CLEANING_PRICES = {
    'Ген.Уборка🧼': 125,
    'Повседневная🧹': 75,
    'Послестрой🛠': 190,
    'Мытье окон🧴': 350
}

# Базовая директория проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Токен Telegram бота (замените 'YOUR_TELEGRAM_BOT_TOKEN' на ваш реальный токен)
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7363733923:AAHKPw_fvjG2F3PBE2XP6Sj49u04uy7wpZE')

# Проверка наличия токена
if TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN':
    logger.warning("Используется токен по умолчанию. Пожалуйста, замените его на реальный токен для продакшена.")
