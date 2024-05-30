import pika
import json

class BotMessageBroker():
    """
    A class to manage message brokering between bot and parser using RabbitMQ.

    Attributes:
        connection (pika.BlockingConnection): The connection to the RabbitMQ server.
        channel (pika.BlockingConnection.channel): The channel for RabbitMQ operations.
        mq (dict): A dictionary to hold any additional message queue configurations.
    """

    def __init__(self):
        """
        Initializes the BotMessageBroker, setting up the RabbitMQ connection and declaring necessary queues.
        """
        connection_params = pika.ConnectionParameters(
            host='rabbit-1'
        )

        self.connection = pika.BlockingConnection(connection_params)

        self.channel = self.connection.channel()

        self.channel.queue_declare(queue='bot2parser_queue')
        self.channel.queue_declare(queue='parser_info_queue')
        self.channel.queue_declare(queue='parser2bot_queue')

        self.mq = {}
    
    def send_message2bot2parser_queue(self, user, pair1_name, pair2_name, check_value, condition_flag):
        """
        Sends a message to the 'bot2parser_queue'.

        Args:
            user (str): The username of the user.
            pair1_name (str): The name of the first currency pair.
            pair2_name (str): The name of the second currency pair.
            check_value (float): The value to check against.
            condition_flag (bool): The condition flag indicating whether to check if the value is greater or less.
        """
        self.channel.basic_publish(
            exchange='',
            routing_key='bot2parser_queue',
            body=json.dumps([user, pair1_name, pair2_name, check_value, condition_flag])
        )

    async def ack_channel(self, method_frame, body, callback, *callback_args):
        """
        Acknowledges a message and calls the provided callback with the message data.

        Args:
            method_frame (pika.frame.Method): The method frame containing the delivery tag.
            body (str): The body of the message.
            callback (function): The callback function to process the message.
            *callback_args: Additional arguments to pass to the callback.
        """
        if method_frame:
            message = json.loads(body)

            self.channel.basic_ack(method_frame.delivery_tag)

            await callback(*callback_args, message)
    
    async def read_message_from_parser2bot_queue(self, callback, bot):
        """
        Reads a message from the 'parser2bot_queue' and processes it with the provided callback.

        Args:
            callback (function): The callback function to process the message.
            bot (AsyncTeleBot): The bot instance to pass to the callback.
        """
        method_frame, _, body = self.channel.basic_get('parser2bot_queue')
        await self.ack_channel(method_frame, body, callback, bot)
    
    async def read_message_from_parser_info_queue(self, callback, bot):
        """
        Reads a message from the 'parser_info_queue' and processes it with the provided callback.

        Args:
            callback (function): The callback function to process the message.
            bot (AsyncTeleBot): The bot instance to pass to the callback.
        """
        method_frame, header_frame, body = self.channel.basic_get('parser_info_queue')
        await self.ack_channel(method_frame, body, callback, bot)

