from bot_message_broker import BotMessageBroker
from reply_actions import BaseReplyAction, ButtonReply, ValueReply, EndReply, ErrorReplyAction
from utils import get_currency_pair_value

import json

class UserMessageProcessor():
    """
    A class to process user messages and interact with a Telegram bot.

    Attributes:
        bot (telebot.TeleBot): The bot instance.
        user (str): The user identifier.
        username (str): The username of the user.
        bot_message_broker (BotMessageBroker): An instance of the BotMessageBroker for sending messages.
        currencies (dict): A dictionary of available currencies.
        message_templates (dict): A dictionary of message templates.
        message_map (dict): A dictionary representing the message map for replies.
        message_coords (list): A list of message coordinates.
        message_data (dict): A dictionary storing data from messages.
    """

    def __init__(self, bot, bot_message_broker: BotMessageBroker, user, username, currencies):
        """
        Initialize the UserMessageProcessor with bot, message broker, user details, and currencies.

        Args:
            bot (telebot.TeleBot): The bot instance.
            bot_message_broker (BotMessageBroker): The bot message broker instance.
            user (str): The user identifier.
            username (str): The username of the user.
            currencies (dict): A dictionary of available currencies.
        """
        self.bot = bot
        self.user = user
        self.username = username
        self.bot_message_broker = bot_message_broker

        self.update_currencies(currencies)
        
        self.update_message_map()
        
        self.message_templates = {
            "check_value": [None, 5]
        }

        self.set_start_message_data()
    
    def update_currencies(self, currencies):
        """
        Update the available currencies and pair names.

        Args:
            currencies (dict): A dictionary of available currencies.
        """
        self.currencies = currencies

        self.pair_names = list(currencies.keys())
        
        self.update_message_map()

    def get_pair_value(self, pair1_name, pair2_name=None):
        """
        Get the value of a currency pair.

        Args:
            pair1_name (str): The name of the first currency in the pair.
            pair2_name (str, optional): The name of the second currency in the pair. Defaults to 'USDC'.

        Returns:
            str: A string representing the value of the currency pair or an error message.
        """
        if pair1_name not in self.currencies:
            return f'... The specified cryptocurrency pair was not found! I couldn`t find "{pair1_name}"'
        if pair2_name is None:
            pair2_name = 'USDC'
        if pair2_name not in self.currencies:
            return f'... The specified cryptocurrency pair was not found! I couldn`t find "{pair2_name}"'
        
        pair_value = get_currency_pair_value(self.currencies[pair1_name], self.currencies[pair2_name])
        if pair_value is None:
            return f'... The value of the cryptocurrency "{pair2_name}" is 0 USDC, calculation cannot be performed! If you insist, the result tends towards ∞ {pair2_name}, which is meaningless.'
        
        return f': {pair_value} {pair2_name}'


    def update_message_map(self):
        """
        Update the message map for the user interactions.
        """
        self.message_map = {
            "bot_message": "Select what you want to do",
            "error_message": "I can't do '<error_value>', but I can respond to the following messages:\n<true_result>",
            "message_data": None,
            "message_action": None,
            "type": ButtonReply,
            "reply_actions": {
                "Set a notification": {
                    "bot_message": "Alright, enter the cryptocurrency you want to monitor",
                    "error_message": "The cryptocurrency you entered <error_value> is not available, please try choosing from the available ones:\n(<true_result>)",
                    "message_data": "pair1_name",
                    "message_action": None,
                    "type": ButtonReply,
                    "reply_actions": {
                        pair1_name: {
                            "bot_message": f"Alright, you entered {pair1_name}, which cryptocurrency would you like to set the notification for?",
                            "error_message": "The cryptocurrency you entered <error_value> is not available, please try choosing from the available ones:\n(<true_result>)",
                            "message_data": "pair2_name",
                            "message_action": None,
                            "type": ButtonReply,
                            "reply_actions": {
                                pair2_name: {
                                    "bot_message": f"You set the pair {pair1_name}/{pair2_name}, do you want to be notified when the price is higher, lower, or crosses your value?\n" \
                                        f"The current rate for {pair1_name}/{pair2_name} is{self.get_pair_value(pair1_name, pair2_name)}",
                                    "error_message": f"The value check type you entered (<error_value>) doesn't match any of the suggested types.\nOptions for value check types:\n(<true_result>)",
                                    "message_data": ["condition_flag", {"When exceeds": True, "When is lower than": False, "When crosses": None}],
                                    "message_action": None,
                                    "type": ButtonReply,
                                    "reply_actions": {
                                        f"When {condition_type}": {
                                            "bot_message": f"Name the price at which I should notify you.\n" \
                                                f"The current rate for {pair1_name}/{pair2_name} is{self.get_pair_value(pair1_name, pair2_name)}",
                                            "error_message": "The price you entered (<error_value>) is incorrect, please check what you entered and try again.\n" \
                                                f"The entered price must be a valid positive integer greater than 0 and less than 10^18 (1000000000000000000) and should not contain extra symbols except '.', ',', " \
                                                f"a single cryptocurrency name prefixed by a space, and a space character.\n" \
                                                f"Examples of correct prices: ['1', '12345', '0.5', '1234567890.0123456789', '100000000000000000 USDC', '1.05 BTC']",
                                            "message_data": "check_value",
                                            "message_action": lambda message_data: self.bot_message_broker.send_message2bot2parser_queue(**message_data),
                                            "type": ValueReply,
                                            "reply_actions": {
                                                "": {
                                                    "bot_message": f"Alright, you set the price <check_value> {pair2_name} for the cryptocurrency pair {pair1_name}/{pair2_name}. " \
                                                        f"I will notify you when the current price " \
                                                        f"{str({'exceeds': f'{condition_type}', 'is lower than': f'{condition_type}', 'crosses': f'{condition_type}'}[condition_type])} the set value.\n" \
                                                        f"The current rate for {pair1_name}/{pair2_name} is{self.get_pair_value(pair1_name, pair2_name)}",
                                                    "error_message": "It seems I encountered a strange problem, so I will just show you the message you sent (<error_value>) and what " \
                                                        "I somehow consider correct (<true_result>).\n" \
                                                        "Sorry for this mistake, as this conversation should have ended, but the following issue occurred:\n'<exception>'",
                                                    "message_data": None,
                                                    "message_action": None,
                                                    "type": EndReply,
                                                    "reply_actions": None
                                                }
                                            }
                                        }
                                        for condition_type in [
                                            "exceeds",
                                            "is lower than",
                                            "crosses"
                                        ]
                                    }
                                }
                                for pair2_name in self.pair_names if pair2_name != pair1_name
                            }
                        }
                        for pair1_name in self.pair_names
                    }
                },
                "Get the current rate": {
                    "bot_message": "Alright, enter the cryptocurrency you want to monitor",
                    "error_message": "The cryptocurrency you entered <error_value> is not available, please try choosing from the available ones:\n(<true_result>)",
                    "message_data": "pair1_name",
                    "message_action": None,
                    "type": ButtonReply,
                    "reply_actions": {
                        pair1_name: {
                            "bot_message": f"Alright, you entered {pair1_name}, which cryptocurrency would you like to know the rate for?",
                            "error_message": "The cryptocurrency you entered <error_value> is not available, please try choosing from the available ones:\n(<true_result>)",
                            "message_data": "pair2_name",
                            "message_action": None,
                            "type": ButtonReply,
                            "reply_actions": {
                                pair2_name: {
                                    "bot_message": f"Alright, the current rate for {pair1_name}/{pair2_name} is{self.get_pair_value(pair1_name, pair2_name)}",
                                    "error_message": "It seems I encountered a strange problem, so I will just show you the message you sent (<error_value>) and what I somehow consider correct " \
                                        "(<true_result>).\nSorry for this mistake, as this conversation should have ended, but the following issue occurred:\n'<exception>'",
                                    "message_data": None,
                                    "message_action": None,
                                    "type": EndReply,
                                    "reply_actions": None
                                }
                                for pair2_name in self.pair_names if pair2_name != pair1_name
                            }
                        }
                        for pair1_name in self.pair_names
                    }
                }
            }
        }


    def try_get_message_type(self, message_map_type, name_reply_actions):
        """
        Try to get the message type based on the message map type.

        Args:
            message_map_type (type): The type of the message map.
            name_reply_actions (list): A list of reply actions.
        """
        if isinstance(message_map_type, BaseReplyAction) is False or type(message_map_type) == BaseReplyAction:
            self.message_type = ErrorReplyAction(name_reply_actions, self.message_templates, self.currencies)
            
        self.message_type = message_map_type(name_reply_actions, self.message_templates, self.currencies)


    def set_start_message_data(self):
        """
        Set the initial message data and message coordinates.
        """
        self.message_coords = []

        self.message_data = {
            "user": [self.user, self.username],
            "pair1_name": None,
            "pair2_name": None,
            "condition_flag": None,
            "check_value": None
        }

        self.try_get_message_type(self.message_map["type"], [name_reply_action for name_reply_action in self.message_map["reply_actions"]])


    def get_message_info(self):
        """
        Get the current message information based on the message coordinates.

        Returns:
            dict or None: The current message information or None if not found.
        """
        result_element = self.message_map
        for message_coordinate in self.message_coords:
            result_element = result_element['reply_actions'][message_coordinate]

            if result_element is None:
                return None
        
        return result_element


    def set_message_type(self, now_message_info):
        """
        Set the message type based on the current message information.

        Args:
            now_message_info (dict): The current message information.
        """
        if now_message_info["reply_actions"] is None:
            name_reply_actions = None
        else:
            name_reply_actions = [name_reply_action for name_reply_action in now_message_info["reply_actions"]]

        self.try_get_message_type(now_message_info["type"], name_reply_actions)


    def reply_message(self, message):
        """
        Generate a reply message based on the current message type and message information.

        Args:
            message (telebot.types.Message): The received message.

        Returns:
            tuple: Arguments and keyword arguments for sending the reply message.
        """
        message_info = self.get_message_info()
        return self.message_type.reply(self.bot, message, message_info["bot_message"])


    def process_message_data(self, message, message_data=None):
        """
        Process the data from the received message.

        Args:
            message (telebot.types.Message): The received message.
            message_data (list|str, optional): The type of message data to process. Defaults to None.
        """
        if message_data is not None:
            if isinstance(message_data, list) is False:
                self.message_data[message_data] = self.message_type.get_data(message.text)
            else:
                self.message_data[message_data[0]] = self.message_type.get_data(message.text, template=message_data[1])
    
    
    def handle_message_action(self, message_action=None):
        """
        Handle the message action if provided.

        Args:
            message_action (callable, optional): The message action to handle. Defaults to None.
        """
        if message_action is not None:
            message_action(self.message_data)


    def check_message(self, message=None):
        """
        Check the validity of the received message and process it accordingly.

        Args:
            message (telebot.types.Message, optional): The received message. Defaults to None.

        Returns:
            tuple: A tuple containing a boolean indicating the validity of the message, error message arguments, and keyword arguments.
        """
        message_info = self.get_message_info()
        exception = None

        if message_info is None:
            self.set_start_message_data()
            return None

        try:
            is_valid, message_coordinate = self.message_type.try_get_message_coordinate(message.text)
            if is_valid is True:
                self.process_message_data(message, message_info["message_data"])

                self.handle_message_action(message_info["message_action"])
                
                self.message_coords.append(message_coordinate)
                message_info = self.get_message_info()

                if message_info is None:
                    self.set_start_message_data()

                self.set_message_type(message_info)
                self.message_type.set_templates(message.text, self.message_coords)

                return True, None, None
        except Exception as exception:
            exception = exception
            
        error_message_args, error_message_kwargs = self.message_type.reply_error(self.bot, message, message_info["error_message"], error_result=message.text, exception=exception)
        
        return False, error_message_args, error_message_kwargs