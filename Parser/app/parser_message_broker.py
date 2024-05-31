import pika
import json
import os

class ParserMessageBroker():
    """
    A class to handle message brokering between different components using RabbitMQ.
    It handles reading from and writing to queues, as well as managing a cache of message queues.

    Attributes:
        parser_docker_logger (ParserLogger): Logger for recording events.
        path_to_mq_cache (str): Path to the message queue cache file.
        connection (pika.BlockingConnection): RabbitMQ connection.
        channel (pika.BlockingConnection.channel): RabbitMQ channel.
        mq (dict): In-memory message queue.
    """

    condition_flag = {
        True: "bigger than",
        False: "lower than",
        None: "will cross"
    }

    def __init__(self, parser_docker_logger, path_to_mq_cache='mq_cache.json') -> None:
        """
        Initialize the ParserMessageBroker with a logger and optional path to the cache file.

        Args:
            parser_docker_logger (ParserLogger): Logger for recording events.
            path_to_mq_cache (str, optional): Path to the message queue cache file. Defaults to 'mq_cache.json'.
        """
        self.parser_docker_logger = parser_docker_logger
        connection_params = pika.ConnectionParameters(
            host='rabbit-1'
        )

        self.connection = pika.BlockingConnection(connection_params)

        self.path_to_mq_cache = path_to_mq_cache

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='bot2parser_queue')
        self.channel.queue_declare(queue='parser2bot_queue')
        self.channel.queue_declare(queue='parser_info_queue')

        self.load_mq_cache(is_width_auto_update=False)

    def load_mq_cache(self, is_width_auto_update=True):
        """
        Load the message queue cache from a file. Optionally update the in-memory queue with the loaded data.

        Args:
            is_width_auto_update (bool, optional): If True, merge loaded data with in-memory queue. Defaults to True.
        """
        if os.path.exists(self.path_to_mq_cache):
            with open(self.path_to_mq_cache, 'r', encoding="utf-8") as cash_fp:
                mq = json.load(cash_fp)

            if is_width_auto_update is True:
                for pair1_name in mq:
                    if pair1_name not in self.mq:
                        self.mq[pair1_name] = {}

                    for pair2_name in mq[pair1_name]:
                        if pair2_name not in self.mq[pair1_name]:
                            self.mq[pair1_name][pair2_name] = []

                        for condition_id in mq[pair1_name][pair2_name]:
                            if mq[pair1_name][pair2_name][condition_id] not in self.mq[pair1_name][pair2_name]:
                                self.mq[pair1_name][pair2_name].append(mq[pair1_name][pair2_name][condition_id])

                return
            
            self.mq = mq
            return
        
        self.mq = {}
    
    def write_2_mq_cache(self, is_with_load=False):
        """
        Write the in-memory message queue to a cache file. Optionally load the cache before writing.

        Args:
            is_with_load (bool, optional): If True, load the cache before writing. Defaults to False.
        """
        if is_with_load is True:
            self.load_mq_cache()

        with open(self.path_to_mq_cache, 'w', encoding="utf-8") as cash_fp:
            json.dump(self.mq, cash_fp, indent=4)

    def read_message_from_bot2parser_queue(self):
        """
        Read a message from the 'bot2parser_queue', log it, and add it to the in-memory queue.
        """
        method_frame, header_frame, body = self.channel.basic_get('bot2parser_queue')
        if method_frame:
            message = json.loads(body)

            self.parser_docker_logger.add_message_from_queue(message, self.condition_flag[message[4]])
            
            message_data = {
                "user": message[0],
                "check_value": message[3],
                "condition_flag": message[4]
            }
            if message[1] in self.mq:
                if message[2] not in self.mq[message[1]]:
                    self.mq[message[1]][message[2]] = []

                self.mq[message[1]][message[2]].append(message_data)
            else:
                self.mq[message[1]] = {message[2]: [message_data]}
                
            self.channel.basic_ack(method_frame.delivery_tag)

            self.write_2_mq_cache()
    
    def set_condition_flag(self, condition_flag, check_value, now_pair_value):
        """
        Determine the condition flag based on the given values.

        Args:
            condition_flag (bool or None): The initial condition flag.
            check_value (float): The value to check against.
            now_pair_value (float): The current value of the pair.

        Returns:
            bool: The determined condition flag.
        """
        return check_value > now_pair_value if condition_flag is None else condition_flag

    def send_message2parser2bot_queue(self, pair1_name, pair2_name, condition_id, now_pair_value, pair1_keys, pair2_keys):
        """
        Send a message to the 'parser2bot_queue' and update the in-memory queue accordingly.

        Args:
            pair1_name (str): The first currency in the pair.
            pair2_name (str): The second currency in the pair.
            condition_id (int): The ID of the condition to check.
            now_pair_value (float): The current value of the currency pair.
            pair1_keys (list): List of first currency keys.
            pair2_keys (list): List of second currency keys.

        Returns:
            tuple: Updated pair1_keys and pair2_keys.
        """
        message_data = self.mq[pair1_name][pair2_name][condition_id]
        out_message = {
            "user": message_data["user"],
            "pair1_name": pair1_name,
            "pair2_name": pair2_name,
            "condition_flag": message_data["condition_flag"],
            "check_value": message_data["check_value"],
            "now_pair_value": now_pair_value
        }
        self.channel.basic_publish(
            exchange='',
            routing_key='parser2bot_queue',
            body=json.dumps(out_message)
        )

        self.parser_docker_logger.add_message_to_queue(out_message)

        del self.mq[pair1_name][pair2_name][condition_id]


        if len(self.mq[pair1_name][pair2_name]) == 0:
            del self.mq[pair1_name][pair2_name]
            del pair2_keys[pair2_keys.index(pair2_name)]

            if len(self.mq[pair1_name]) == 0:
                del self.mq[pair1_name]
                del pair1_keys[pair1_keys.index(pair1_name)]
        
        self.write_2_mq_cache()

        return pair1_keys, pair2_keys

    def send_message2parser_info_queue(self, currencies):
        """
        Send currency information to the 'parser_info_queue'.

        Args:
            currencies (dict): A dictionary of currency data.
        """
        self.channel.basic_publish(
            exchange='',
            routing_key='parser_info_queue',
            body=json.dumps(currencies)
        )
    
    def close_connection(self):
        """
        Close the RabbitMQ connection after writing the in-memory queue to the cache.
        """
        self.write_2_mq_cache()

        self.connection.close()