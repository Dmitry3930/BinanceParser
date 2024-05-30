from binance_parser import BinanceParser
from parser_message_broker import ParserMessageBroker
from parser_logger import ParserLogger

from time import sleep

class BinanceMessageProcessor():
    """
    Class for processing messages related to Binance currency pairs.

    Attributes:
        parser_docker_logger (ParserLogger): Logger for recording events.
        parser (BinanceParser): Parser for retrieving currency pair data.
        message_broker (ParserMessageBroker): Message broker for handling message queues.
        delay (int): Delay between message processing cycles.
    """

    def __init__(self, parser_docker_logger, delay=1) -> None:
        """
        Initializes BinanceMessageProcessor with the given logger and delay.

        Args:
            parser_docker_logger (ParserLogger): Logger for recording events.
            delay (int): Delay between message processing cycles (in seconds).
        """
        self.parser_docker_logger = parser_docker_logger
        self.parser = BinanceParser(self.parser_docker_logger)

        self.message_broker = ParserMessageBroker(self.parser_docker_logger)

        self.delay = delay

    @staticmethod
    def condition_check(condition_flag, value1, value2):
        """
        Checks a condition based on the given flag and values.

        Args:
            condition_flag (bool): Condition flag.
            value1 (float): First value for comparison.
            value2 (float): Second value for comparison.

        Returns:
            bool: Result of the condition check.
        """
        if condition_flag is True:
            return value1 > value2
        return value1 <= value2
    
    def update_condition_flag(self, pair1_keys, pair2_keys, pair1_id, pair2_id, condition_id, now_pair_value, check_value):
        """
        Updates the condition flag for the current currency pair.

        Args:
            pair1_keys (list): List of keys for the first currency pair.
            pair2_keys (list): List of keys for the second currency pair.
            pair1_id (int): Index of the first currency pair.
            pair2_id (int): Index of the second currency pair.
            condition_id (int): Index of the condition.
            now_pair_value (float): Current value of the currency pair.
            check_value (float): Value for condition checking.
        """
        self.message_broker.mq[pair1_keys[pair1_id]][pair2_keys[pair2_id]][condition_id]["condition_flag"] = self.message_broker.set_condition_flag(
            self.message_broker.mq[pair1_keys[pair1_id]][pair2_keys[pair2_id]][condition_id]["condition_flag"], 
            check_value, 
            now_pair_value
        )
    
    def process_message(self, pair1_keys, pair2_keys, pair1_id, pair2_id, condition_id, now_pair_value):
        """
        Processes a message for the current currency pair and condition.

        Args:
            pair1_keys (list): List of keys for the first currency pair.
            pair2_keys (list): List of keys for the second currency pair.
            pair1_id (int): Index of the first currency pair.
            pair2_id (int): Index of the second currency pair.
            condition_id (int): Index of the condition.
            now_pair_value (float): Current value of the currency pair.

        Returns:
            bool: Result of the condition check.
        """
        check_value = self.message_broker.mq[pair1_keys[pair1_id]][pair2_keys[pair2_id]][condition_id]["check_value"]

        self.update_condition_flag(pair1_keys, pair2_keys, pair1_id, pair2_id, condition_id, now_pair_value, check_value)

        message = self.message_broker.mq[pair1_keys[pair1_id]][pair2_keys[pair2_id]][condition_id]
        
        condition_result = self.condition_check(message["condition_flag"], now_pair_value, check_value)
        self.parser_docker_logger.add_message_condition(
            message, 
            pair1_keys[pair1_id], 
            pair2_keys[pair2_id], 
            condition_result, 
            now_pair_value, 
            check_value
        )
        return condition_result
    
    def process_conditions(self, pair1_keys, pair2_keys, pair1_id, pair2_id, currencies):
        """
        Processes all conditions for the current currency pair.

        Args:
            pair1_keys (list): List of keys for the first currency pair.
            pair2_keys (list): List of keys for the second currency pair.
            pair1_id (int): Index of the first currency pair.
            pair2_id (int): Index of the second currency pair.
            currencies (dict): Dictionary with currency data.
        """
        condition_id = 0
        now_pair_value = self.parser.get_pair(currencies, pair1_keys[pair1_id], pair2_keys[pair2_id])
        if now_pair_value is None:
            self.parser_docker_logger.log_exception(f'Getting pair was unsuccessful. First currency pair name: {pair1_keys[pair1_id]}, second currency pair name: {pair2_keys[pair2_id]}. Process conditions was canceled.')
            return

        while pair1_id < len(pair1_keys) and pair2_id < len(pair2_keys) and condition_id < len(self.message_broker.mq[pair1_keys[pair1_id]][pair2_keys[pair2_id]]):
            condition_result = self.process_message(
                pair1_keys, 
                pair2_keys, 
                pair1_id, 
                pair2_id, 
                condition_id, 
                now_pair_value
            )

            if condition_result is True:
                pair1_keys, pair2_keys = self.message_broker.send_message2parser2bot_queue(
                    pair1_keys[pair1_id], 
                    pair2_keys[pair2_id], 
                    condition_id, 
                    now_pair_value, 
                    pair1_keys, 
                    pair2_keys
                )
            else:
                condition_id += 1
    
    def check_mq(self):
        """
        Checks the message queue and processes conditions for currency pairs.
        """
        currencies = self.parser.get_currencies()

        self.parser_docker_logger.update_currencies(currencies)

        self.message_broker.send_message2parser_info_queue(currencies)
        
        if len(self.message_broker.mq) == 0:
            self.parser_docker_logger.log()
            return
        

        pair1_keys = list(self.message_broker.mq.keys())
        pair1_id = 0
        while pair1_id < len(pair1_keys):
            pair2_keys = list(self.message_broker.mq[pair1_keys[pair1_id]].keys())
            pair2_id = 0
            while pair1_id < len(pair1_keys) and pair2_id < len(pair2_keys):
                self.process_conditions(pair1_keys, pair2_keys, pair1_id, pair2_id, currencies)
                
                pair2_id += 1

            pair1_id += 1

        self.parser_docker_logger.log()

    def process_messages(self):
        """
        Main loop for processing messages from the queue.
        """
        while True:
            self.message_broker.read_message_from_bot2parser_queue()
            self.check_mq()
            sleep(self.delay)

    def __call__(self):
        """
        Starts the main message processing loop, handling KeyboardInterrupt.
        """
        try:
            self.process_messages()
        except KeyboardInterrupt:
            self.message_broker.close_connection()


if __name__=='__main__':
    parser_docker_logger = ParserLogger()
    binance_message_processor = BinanceMessageProcessor(parser_docker_logger)

    binance_message_processor()