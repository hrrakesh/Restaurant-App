import datetime 
import random
import string

def get_alpha_char():
    random_alpha = ''.join(random.choices(string.ascii_letters, k=4))
    return random_alpha

def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d') # 20250115 + pk
    order_number = get_alpha_char()+ '-' + current_datetime + str(pk)
    return order_number

def get_one_usd():
    conversion_fee = 0
    return 85.0 + conversion_fee