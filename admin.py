from telegram import Update  # Для обработки обновлений
from telegram.ext import ContextTypes  # Для работы с контекстом
from utils import send_message  # Для отправки сообщений
from menu_tree import MENU_TREE  # Для работы с деревом состояний
import logging  # Для логирования

logger = logging.getLogger(__name__)

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает админ-панель."""
    # Получаем состояние админ-панели из MENU_TREE
    if user_choice in MENU_TREE['admin_menu']['next_state']:
        next_state = MENU_TREE['admin_menu']['next_state'][user_choice]
        context.user_data['state'] = next_state
        # Отправляем следующее сообщение на основе выбранного состояния
        await send_message(update, context, MENU_TREE[next_state]['message'], MENU_TREE[next_state]['options'])
    else:
        # Если команда не распознана, просим выбрать опцию заново
        await send_message(update, context, "Выберите опцию в админ-панели.", MENU_TREE['admin_menu']['options'])


async def moderation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user_choice: str) -> None:
    """Обрабатывает панель модерации."""
    # Если выбрано "Админ меню", возвращаемся в админ-панель
    if user_choice == 'Админ меню':
        context.user_data['state'] = 'admin_menu'
        await send_message(update, context, MENU_TREE['admin_menu']['message'], MENU_TREE['admin_menu']['options'])
    else:
        # Если команда не распознана, просим вернуться в модерацию
        await send_message(update, context, "Вернитесь в админ-панель.", MENU_TREE['moderation_menu']['options'])



