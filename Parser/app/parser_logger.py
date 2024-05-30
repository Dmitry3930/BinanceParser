from utils import try_get_stable_coin_dollar_value
import logging

class ParserLogger():
    """
    A class for logging parser-related information.

    Args:
        is_print (bool): Flag indicating whether log messages should be printed in addition to being logged.
    """

    def __init__(self, is_print=False):
        """
        Initializes the ParserLogger object.

        Args:
            is_print (bool): Flag indicating whether log messages should be printed in addition to being logged.
        """
        self.is_print = is_print

        self.logger = logging.getLogger('PARSER')
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s [%(name)-6s] %(levelname)-4s: %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

        self.logger.info('Parser Inited!')
        print('Parser Inited!')

        self.logger.info('')
        print()

        self.currency_logs = []
        self.message_from_queue_logs = []
        self.message_conditions_logs = []
        self.message_to_queue_logs = []

    def update_currencies(self, currencies):
        """
        Updates the log with currency information.

        Args:
            currencies (dict): A dictionary containing currency information.
        """
        self.currency_logs = []

        stable_coin_value, stable_coin_name = try_get_stable_coin_dollar_value(currencies, 'USDC')

        for currency_name in currencies:
            pair_value = currencies[currency_name] / stable_coin_value

            pair_name = f'{currency_name}/{stable_coin_name}'
            if stable_coin_name == '$':
                pair_name = currency_name
                
            self.currency_logs.append(
                f'    {pair_name}: {pair_value} {stable_coin_name}'
            )
    
    @staticmethod
    def _get_condition_type_string(message):
        """
        Helper method to get the condition type string.

        Args:
            message (dict): The message dictionary.

        Returns:
            str: The condition type string.
        """
        if message['condition_flag'] is True:
            return 'bigger'
        return 'lower'

    def add_message_condition(
        self, 
        message, 
        pair1_name, 
        pair2_name, 
        condition_result, 
        now_pair_value, 
        check_value
    ):
        """
        Adds a message condition to the log.

        Args:
            message (dict): The message dictionary.
            pair1_name (str): The name of the first pair.
            pair2_name (str): The name of the second pair.
            condition_result (bool): The condition result.
            now_pair_value (float): The current pair value.
            check_value (float): The check value.
        """
        condition_type_string = self._get_condition_type_string(message)
        self.message_conditions_logs.append(
            f'    {message["user"][1]} ({message["user"][0]}): ' \
            f'now value of {pair1_name} is {now_pair_value} {pair2_name}, ' \
            f'is {condition_type_string}: {condition_result}, ' \
            f'check value: {check_value} {pair2_name}'
        )
    
    def add_message_from_queue(self, message, condition_flag):
        """
        Adds a message from the queue to the log.

        Args:
            message (tuple): The message tuple.
            condition_flag (bool): The condition flag.
        """
        self.message_from_queue_logs.append(
            f'    {message[0][1]} ({message[0][0]}) send message: ' \
            f'check {message[1]} is {condition_flag}: {message[3]} {message[2]}'
        )
    

    def add_message_to_queue(self, message):
        """
        Adds a message to the queue log.

        Args:
            message (dict): The message dictionary.
        """
        condition_type_string = self._get_condition_type_string(message)

        self.message_to_queue_logs.append(
            f'    {message["user"][1]} ({message["user"][0]}), ' \
            f'The {message["pair1_name"]} is {condition_type_string} ' \
            f'than {message["check_value"]} {message["pair2_name"]} ' \
            f'and equals {message["now_pair_value"]} {message["pair2_name"]}'
        )


    def _log_string(self, log_message):
        """
        Logs a message.

        Args:
            log_message (str): The message to log.
        """
        self.logger.info(log_message)

        if self.is_print is True:
            print(log_message)


    def log(self):
        """
        Logs the collected information.
        """
        self._log_string('#################################################')

        self._log_string('Now currencies: [')
        for currency_log in self.currency_logs:
            self._log_string(currency_log)
        self._log_string(']')

        self._log_string('')

        self._log_string('Gated messages: [')
        for message_from_queue_log in self.message_from_queue_logs:
            self._log_string(message_from_queue_log)
        self._log_string(']')

        self._log_string('')
        
        self._log_string('Now user`s conditions: [')
        for message_condition_log in self.message_conditions_logs:
            self._log_string(message_condition_log)
        self._log_string(']')

        self._log_string('')
        
        self._log_string('Sended messages: [')
        for message_to_queue_log in self.message_to_queue_logs:
            self._log_string(message_to_queue_log)
        self._log_string(']')

        self._log_string('#################################################')
        self._log_string('')

        self.message_from_queue_logs = []
        self.message_conditions_logs = []
        self.message_to_queue_logs = []
    
    def log_exception(self, exception_message):
        """
        Log an exception message.

        Args:
            exception_message (str): The exception message to log.
        """
        self._log_string(f'EXCEPTION: "{exception_message}"')

    def log_info(self, info_message):
        """
        Log an informational message.

        Args:
            info_message (str): The informational message to log.
        """
        self._log_string(f'INFO: "{info_message}"')
        
    def exit_message(self):
        """
        Logs the exit message.
        """
        self._log_string('Parser Exited!')