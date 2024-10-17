import requests

# Ваш Google Analytics Tracking ID
GA_TRACKING_ID = 'G-WY3084MYCK'  # Замените на ваш ID

# Функция для отправки события в Google Analytics
def send_event_to_ga(category, action, label):
    data = {
        'v': '1',  # Версия протокола
        'tid': GA_TRACKING_ID,  # Ваш Tracking ID
        'cid': '555',  # Уникальный идентификатор клиента (можно генерировать или использовать user_id)
        't': 'event',  # Тип запроса - событие
        'ec': category,  # Категория события
        'ea': action,  # Действие события
        'el': label,  # Ярлык события
    }
    response = requests.post('https://www.google-analytics.com/collect', data=data)
    if response.status_code == 200:
        print(f"Событие отправлено в Google Analytics: {response.status_code}")
    else:
        print(f"Ошибка отправки события: {response.status_code}")
