from datetime import datetime
from random import randint

def parse_templates(string_data: str, **kwargs):
    """
    Replace template placeholders in the given string with corresponding values from kwargs.

    Args:
        string_data (str): The string containing template placeholders in the format <placeholder>.
        **kwargs: Key-value pairs where the key is the template placeholder name and the value is the replacement.

    Returns:
        str: The string with template placeholders replaced by their corresponding values.
    """
    result = string_data
    for template_name in kwargs:
        result = result.replace(f'<{template_name}>', f'{kwargs[template_name]}')
    return result

def get_message_id():
    """
    Generate a unique message ID based on the current timestamp and a random number.

    The format of the message ID is: 'timestamp_in_milliseconds_random_number'.

    Returns:
        str: The generated unique message ID.
    """
    return f'{datetime.timestamp(datetime.now())*1000}_{randint(100000000, 999999999)}'.rjust(28)

def get_currency_pair_value(pair1, pair2):
    """
    Calculate the value of a currency pair.

    If the second currency value (pair2) is very close to zero or below, return None.

    Args:
        pair1 (float): The value of the first currency.
        pair2 (float): The value of the second currency.

    Returns:
        float or None: The calculated currency pair value, rounded to 3 decimal places if greater than 0.001, 
                       or the full value if less than or equal to 0.001. Returns None if pair2 is too small.
    """
    if pair2 <= 0.000000000000000001:
        return None
    
    full_pair_value = pair1 / pair2
    rounded_pair_value = round(full_pair_value, 3)

    if rounded_pair_value > 0.001:
        return rounded_pair_value
    else:
        return full_pair_value