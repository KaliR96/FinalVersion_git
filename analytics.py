import requests

# Ваш Google Analytics Tracking ID и API секрет
GA_MEASUREMENT_ID = 'G-WY3084MYCK'  # Уникальный идентификатор ресурса GA4
API_SECRET = 'kLplxR5cRKuwGEy9_qj1KQ'  # Секретный ключ для Measurement Protocol


def send_event_to_ga(user_id, category, action, label, username=None):
    """
    Отправляет событие в Google Analytics через Measurement Protocol API.

    Аргументы:
    - user_id (int): Уникальный ID пользователя (например, update.effective_user.id из Telegram API).
    - category (str): Категория события (например, "User").
    - action (str): Действие, связанное с событием (например, "ButtonClick").
    - label (str): Дополнительное описание события (например, "Button: ShowPhoneNumber").
    - username (str, optional): Юзернейм пользователя Telegram (если доступен).
    """
    # Формируем тело запроса
    data = {
        'client_id': str(user_id),  # Уникальный идентификатор клиента
        'user_properties': {  # Дополнительные свойства пользователя
            'username': username or 'anonymous',  # Передаем юзернейм или 'anonymous', если юзернейм отсутствует
            'platform': 'Telegram',  # Указываем, что данные с платформы Telegram
        },
        'events': [{
            'name': 'page_view',  # Название события (например, просмотр страницы)
            'params': {
                'page_title': category,  # Категория события
                'page_location': action,  # Действие, связанное с событием
                'page_path': label  # Дополнительная информация о событии
            }
        }]
    }

    # Формируем URL для отправки данных в Google Analytics
    url = f'https://www.google-analytics.com/debug/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={API_SECRET}'


    # Отправляем POST-запрос с данными
    response = requests.post(url, json=data)

    # Проверяем ответ от сервера Google Analytics
    if response.status_code == 200:
        print(f"Событие отправлено в Google Analytics: {response.status_code}")
    else:
        print(f"Ошибка отправки события: {response.status_code}, Ответ: {response.text}")


# Пример использования функции send_event_to_ga
if __name__ == "__main__":
    # Пример отправки события:
    user_id = 0  # Указываем 0 для событий, не связанных с конкретным пользователем
    category = "Bot"  # Категория события
    action = "Start"  # Действие события
    label = "Bot started"  # Дополнительная информация о событии

    # Отправляем событие в Google Analytics
    send_event_to_ga(user_id, category, action, label)
