from settings import MIN_PRICE_DROP

def check_price_drop(old_price, new_price):
    if old_price is None:
        return False
    drop_percent = round((1-new_price / old_price) * 100)

    if drop_percent >= MIN_PRICE_DROP:
        return True
    return False