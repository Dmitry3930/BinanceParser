from bs4 import BeautifulSoup

from selenium import webdriver

class BinanceParser():
    """
    A parser to fetch and process currency data from Binance.

    Attributes:
        parser_docker_logger (ParserLogger): Logger for recording events.
        url (str): URL to fetch currency data from.
        browser (webdriver.PhantomJS): Headless browser instance to scrape data.
    
    Note:
        This parser can take currencies only from first page "https://www.binance.com/en/markets/overview"
    """

    def __init__(self, parser_docker_logger) -> None:
        """
        Initializes the BinanceParser with a logger and sets up the browser.

        Args:
            parser_docker_logger (ParserLogger): Logger for recording events.
        """
        self.parser_docker_logger = parser_docker_logger
        self.url = 'https://www.binance.com/en/markets/overview'
        self.browser = webdriver.PhantomJS()
        self.browser.get(self.url)

    def get_currencies(self):
        """
        Fetches and parses currency data from Binance.

        Tries to scrape the data multiple times in case of failures.

        Returns:
            dict: A dictionary with currency names as keys and tuples of 
                  currency value strings and floats as values.
        """
        is_excepted = False

        max_retries = 5
        retries = 0

        while retries < max_retries:
            self.browser.refresh()
            soup = BeautifulSoup(self.browser.page_source, 'lxml')

            currencies_table = soup.find("div", {"class": "css-1pysja1"})

            try:
                currency_names = currencies_table.find_all("div", {"class": "subtitle3 text-t-primary css-vurnku"})
                currency_values = currencies_table.find_all("div", {"class": "body2 items-center css-18yakpx"})

                currencies = {}
                for currency_name, currency_value in zip(currency_names, currency_values):
                    currencies[currency_name.text] = float(currency_value.text.strip('$').replace(',', ''))

                if is_excepted is True:
                    self.parser_docker_logger.log_info(f'The parser problem was solved!')
                return currencies
            except AttributeError as error:
                is_excepted = True
                self.parser_docker_logger.log_exception(f'The parser had a problem with this url: "{self.url}". Exception: "{error}". Retrying {retries}/{max_retries}...')
                retries += 1
        
        self.parser_docker_logger.log_exception(f'The parser could not resolve the problem after {max_retries} attempts. The result currencies was empty.')
        
        return {}

    def get_pair(self, currencies, first_el_name, second_el_name=None):
        """
        Calculates the value ratio between two currencies.

        Args:
            currencies (dict): Dictionary of currencies and their values.
            first_el_name (str): The name of the first currency.
            second_el_name (str, optional): The name of the second currency. Defaults to None.

        Returns:
            float or None: The value ratio between the two currencies, or None if an error occurred.
        """
        if first_el_name not in currencies:
            self.parser_docker_logger.log_exception(f'The first currency pair name ({first_el_name}) isn`t in currencies dict ({currencies.keys()}). The result was empty. ')
            return None
        first_currency = currencies[first_el_name]

        if second_el_name is None:
            second_currency = 1
        else:
            if second_el_name not in currencies:
                self.parser_docker_logger.log_exception(f'The second currency pair name ({second_el_name}) isn`t in currencies dict ({currencies.keys()}). The result was empty.')
                return None
            second_currency = currencies[second_el_name]
        
        return first_currency / second_currency