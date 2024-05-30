from utils import get_currency_pair_value

CURRENCIES2STR_SIMPLE = 0
CURRENCIES2STR_SHORT = 1
CURRENCIES2STR_LONG = 2
CURRENCIES2STR_FULL = 3

def _get_stable_coin_dollar_value(currencies, stable_coin_name):
    """
    Retrieve the value of a stable coin in the given currencies dictionary.

    Args:
        currencies (dict): A dictionary of currencies and their values.
        stable_coin_name (str): The name of the stable coin to get the value for.

    Returns:
        float: The value of the stable coin if found, otherwise 1.0.
    """
    if stable_coin_name in currencies:
        return currencies[stable_coin_name]
    return 1.0

def _get_currency_value(currencies, currency_name):
    """
    Retrieve the value of a currency relative to USDC.

    Args:
        currencies (dict): A dictionary of currencies and their values.
        currency_name (str): The name of the currency to get the value for.

    Returns:
        str: The rounded value of the currency relative to USDC or 'Not found' if the currency is not in the dictionary.
    """
    if currency_name not in currencies:
        return 'Not found'

    USDC_value = _get_stable_coin_dollar_value(currencies, "USDC")

    pair_value = get_currency_pair_value(currencies[currency_name], USDC_value)
    if pair_value is None:
        return 'Not found'
    
    return str(pair_value)

def set_currencies_to_str(currencies, mode=CURRENCIES2STR_SHORT):
    """
    Convert a dictionary of currencies and their values to a formatted string based on the specified mode.

    Args:
        currencies (dict): A dictionary of currencies and their values.
        mode (int): The mode of formatting. Can be one of CURRENCIES2STR_SIMPLE, CURRENCIES2STR_SHORT, 
                    CURRENCIES2STR_LONG, or CURRENCIES2STR_FULL.

    Returns:
        str: The formatted string representing the currencies and their values.
    """
    result_stroke = [f'Cryptocurrency rates:']

    if mode == CURRENCIES2STR_SIMPLE:
        # Generate a simple description for the bot
        result_stroke = f'A simple bot for displaying cryptocurrency rates and setting notifications'
    elif mode == CURRENCIES2STR_SHORT:
        # Generate a short string with values for a few specific currencies
        for currency_name in ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']:
            currency_str = f' {currency_name}/USDC: {_get_currency_value(currencies, currency_name)},'

            if len(''.join(result_stroke)) + len(currency_str) >= 120:
                break

            result_stroke.append(currency_str)
    elif mode == CURRENCIES2STR_LONG:
        # Generate a longer string with values for all currencies excluding stable coins
        for currency_name in currencies:
            if currency_name in ['USDT', 'USDC', 'DAI']:
                continue

            currency_str = f' {currency_name}/USDC: {_get_currency_value(currencies, currency_name)},'

            if len(''.join(result_stroke)) + len(currency_str) >= 512:
                break

            result_stroke.append(currency_str)
    elif mode == CURRENCIES2STR_FULL:
        # Generate a full HTML formatted string with clickable links for all currencies excluding USDC
        result_stroke = [f'<b>Cryptocurrency rates:</b>']
        for currency_name in currencies:
            if currency_name in ['USDC']:
                continue

            result_stroke.append(
                f'\n<b>{currency_name.rjust(4)}/USDC</b>: ' \
                f'<a href="https://www.binance.com/ru/trade/{currency_name}_USDC?type=spot">{_get_currency_value(currencies, currency_name)} USDC</a> '
            )
    else:
        # Don`t generate anything
        return ''
    
    return str(''.join(result_stroke))[:-1]