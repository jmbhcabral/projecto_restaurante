''' Generate a random code to reset the password. '''

import random


def generate_reset_password_code():
    ''' Generate a random code to reset the password. '''

    # Generate a random code
    code = random.randint(100000000, 999999999)
    return code
