# calculator.py

def calculate(price_per_sqm, sqm):
    total_cost = price_per_sqm * sqm

    # Проверка минимальной стоимости
    if total_cost < 1500:
        total_cost = 1500
        formatted_message = (
            f'Стоимость вашей уборки: 1500.00 руб.\n'
            'Это минимальная стоимость заказа.'
        )
    else:
        formatted_message = f'Стоимость вашей уборки: {total_cost:.2f} руб. за {sqm:.2f} кв.м.'

    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }

# Функция для расчета стоимости мытья окон
def calculate_windows(price_per_panel, num_panels):
    total_cost = price_per_panel * num_panels

    # Проверка минимальной стоимости
    if total_cost < 1500:
        total_cost = 1500
        formatted_message = (
            f'Стоимость мытья окон: 1500.00 руб.\n'
            'Это минимальная стоимость заказа.'
        )
    else:
        formatted_message = f'Стоимость мытья окон: {total_cost:.2f} руб. за {num_panels} створок(и).'

    return {
        'total_cost': total_cost,
        'formatted_message': formatted_message
    }
