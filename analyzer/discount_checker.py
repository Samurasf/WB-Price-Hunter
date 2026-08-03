from settings import MIN_RATING, MIN_REVIEWS, MIN_DISCOUNT

def check_product(product):
    if product["reviews"] < MIN_REVIEWS:
        return False 
    if product["rating"] < MIN_RATING:
        return False
    if product["discount"] < MIN_DISCOUNT:
        return False
    return True