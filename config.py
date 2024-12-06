import logging
import os

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ID вашего канала
CHANNEL_ID = -1002249882445

# Укажите ваш Telegram ID
ADMIN_ID = 1238802718  # Замените на ваш реальный Telegram ID

# Токен вашего бота
TOKEN = '7971939079:AAE9UlW5kFlmzqoWg3aFSm2HFECaLY_fD8k'  # Укажите токен вашего бота

# Путь к директории, где находится текущий файл
base_dir = os.path.dirname(os.path.abspath(__file__))
