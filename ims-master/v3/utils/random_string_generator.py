import random
import string

def random_string_generator(size=10, chars=string.ascii_letters + string.digits):
    rand_chars = ''
    for time in range(size):
        rand_chars += random.choice(chars)
    return rand_chars
