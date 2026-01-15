''' Generate a random code to reset the password. '''
# djangoapp/utils/generate_reset_password_code.py
#TODO: Refactor this code to return a string for using new db field reset_password_code.
from __future__ import annotations

import random


def generate_reset_password_code():
    ''' Generate a random code to reset the password. '''

    # Generate a random code
    code = random.randint(100000000, 999999999)
    return code
