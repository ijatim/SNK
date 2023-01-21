import string
import random


def get_random_string(length: int = 30) -> str:
    result_str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return result_str
