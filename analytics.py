import requests

# Ваш Google Analytics Tracking ID и API секрет
GA_MEASUREMENT_ID = 'G-WY3084MYCK'
API_SECRET = 'kLplxR5cRKuwGEy9_qj1KQ'

def send_event_to_ga(category, action, label):
    data = {
        'client_id': '555',  # Уникальный идентификатор клиента (например, user_id)
        'events': [{
            'name': 'page_view',  # Используйте 'page_view' для отслеживания просмотров страниц
            'params': {
                'page_title': category,  # Название страницы или экрана
                'page_location': action,  # URL страницы или экрана
                'page_path': label  # Путь к странице
            }
        }]
    }
    url = f'https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={API_SECRET}'
    response = requests.post(url, json=data)

    if response.status_code == 200:
        print(f"Событие отправлено в Google Analytics: {response.status_code}")
    else:
        print(f"Ошибка отправки события: {response.status_code}")
