import random

def generate_card_number():
    min_card_number = 10 ** 15
    max_card_number = (10 ** 16) - 1
    return random.randint(min_card_number, max_card_number)

def generate_cvv():
    return random.randint(100, 999)