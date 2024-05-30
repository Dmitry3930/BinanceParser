def try_get_stable_coin_dollar_value(currencies, stable_coin_name):
    """
    Retrieve the value of a stable coin in the given currencies dictionary.

    Args:
        currencies (dict): A dictionary of currencies and their values.
        stable_coin_name (str): The name of the stable coin to get the value for.

    Returns:
        float: The value of the stable coin if found, otherwise 1.0.
    """
    if stable_coin_name in currencies:
        return currencies[stable_coin_name], stable_coin_name
    return 1.0, '$'