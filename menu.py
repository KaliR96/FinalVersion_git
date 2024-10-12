# menu.py

from data import CLEANING_DETAILS

MENU_TREE = {
    'main_menu': {
        'message': (
            'Привет! Я Вера, твоя фея чистоты.\n\n'
            'Мой робот-уборщик поможет:\n\n'
            '🔍 Ознакомиться с моими услугами\n\n'
            '🧮 Рассчитать стоимость уборки\n\n'
            '🚗 Заказать клининг на дом\n\n'
            '📞 Связаться со мной.'
        ),
        'options': [
            ['Тарифы🏷️', 'Калькулятор🧮'],
            ['Связаться📞', 'Отзывы💬'],
            ['Полезная информация📢']
        ],
        'next_state': {
            'Тарифы🏷️': 'show_tariffs',
            'Калькулятор🧮': 'calculator_menu',
            'Связаться📞': 'contact',
            'Отзывы💬': 'reviews_menu',
            'Полезная информация📢': 'useful_info'
        }
    },
    'useful_info': {
        'message': 'Посетите наш канал для получения последних новостей, акций и розыгрышей!',
        'options': ['Главное меню🔙'],
        'next_state': {
            'Главное меню🔙': 'main_menu'
        }
    },
    'admin_menu': {
        'message': 'Админ-панель:\nВыберите действие:',
        'options': ['Модерация'],
        'next_state': {
            'Модерация': 'moderation_menu',
        }
    },
    'moderation_menu': {
        'message': 'Вы всегда можете вернуться в админ меню :)',
        'options': ['Админ меню'],
        'next_state': {
            'Админ меню': 'admin_menu'
        }
    },
    'reviews_menu': {
        'message': 'Что вы хотите сделать?',
        'options': ['Написать отзыв', 'Посмотреть Отзывы💬', 'Главное меню🔙'],
        'next_state': {
            'Написать отзыв': 'write_review',
            'Посмотреть Отзывы💬': 'view_reviews',
            'Главное меню🔙': 'main_menu'
        }
    },
    'view_reviews': {
        'message': 'Просмотрите все отзывы на нашем канале:',
        'options': ['Перейти к каналу', 'Главное меню🔙'],
        'next_state': {
            'Перейти к каналу': 'open_channel',
            'Главное меню🔙': 'reviews_menu'
        }
    },
    'write_review': {
        'message': 'Пожалуйста, напишите ваш отзыв💬:',
        'options': ['Главное меню🔙'],
        'next_state': {
            'Главное меню🔙': 'main_menu'
        }
    },
    'show_tariffs': {
        'message': 'Выберите тариф для получения подробностей:',
        'options': [
            ['Ген.Уборка🧼', 'Повседневная🧹'],
            ['Послестрой🛠', 'Мытье окон🧴'],
            ['Главное меню🔙']
        ],
        'next_state': {
            'Ген.Уборка🧼': 'detail_Ген.Уборка🧼',
            'Повседневная🧹': 'detail_Повседневная🧹',
            'Послестрой🛠': 'detail_Послестрой🛠',
            'Мытье окон🧴': 'detail_Мытье окон🧴',
            'Главное меню🔙': 'main_menu'
        }
    },
    'calculator_menu': {
        'message': 'Выберите тип уборки🧺:',
        'options': [
            ['Ген.Уборка🧼', 'Повседневная🧹'],
            ['Послестрой🛠', 'Мытье окон🧴'],
            ['Главное меню🔙']
        ],
        'next_state': {
            'Ген.Уборка🧼': 'enter_square_meters',
            'Повседневная🧹': 'enter_square_meters',
            'Послестрой🛠': 'enter_square_meters',
            'Мытье окон🧴': 'enter_window_panels',
            'Главное меню🔙': 'main_menu'
        }
    },
    'enter_square_meters': {
        'message': 'Введите количество квадратных метров,\nкоторые нужно убрать.',
        'options': ['Главное меню🔙'],
        'next_state': {
            'add_extras': 'add_extras'
        }
    },
    'enter_window_panels': {
        'message': 'Введите количество оконных створок:',
        'options': ['Главное меню🔙'],
        'next_state': {
            'calculate_result': 'calculate_result'
        }
    },
    'add_extras': {
        'message': 'Выберите дополнительные услуги или завершите расчет:',
        'options': [
            ['Глажка белья', 'Стирка белья'],
            ['Почистить лоток', 'Уход за цветами'],
            ['Мытье окон🧴(1 створка)'],
            ['Связаться📞'],
            ['Главное меню🔙'],
        ],
        'next_state': {
            'Глажка белья': 'add_extras',
            'Стирка белья': 'add_extras',
            'Почистить лоток': 'add_extras',
            'Уход за цветами': 'add_extras',
            'Мытье окон🧴(1 створка)': 'add_extras',
            'Связаться📞': 'contact',
            'Главное меню🔙': 'main_menu'
        }
    },
    'calculate_result': {
        'options': ['Главное меню🔙', 'Связаться📞'],
        'next_state': {
            'Главное меню🔙': 'main_menu',
            'Связаться📞': 'contact'
        }
    },
    'contact': {
        'message': 'Связаться📞 со мной вы можете через следующие каналы:',
        'options': ['Главное меню🔙'],
        'next_state': {
            'Главное меню🔙': 'main_menu'
        }
    }
}

# Динамическое добавление состояний для каждого тарифа
for tariff_name, details in CLEANING_DETAILS.items():
    MENU_TREE[f'detail_{tariff_name}'] = {
        'message': details['details_text'],
        'image_path': details['image_path'],
        'options': ['Калькулятор🧮', 'Назад'],
        'next_state': {
            'Калькулятор🧮': 'calculator_menu',
            'Назад': 'show_tariffs'
        }
    }
