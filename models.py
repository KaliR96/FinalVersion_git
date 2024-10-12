
from config import CLEANING_PRICES, CLEANING_DETAILS

def calculate_cleaning_cost(service_type, square_meters):
    # Function to calculate the cleaning cost based on square meters and service type
    price_per_meter = CLEANING_PRICES.get(service_type)
    if price_per_meter:
        return price_per_meter * square_meters
    return None
