from user_message_processor import UserMessageProcessor

class UserManager():
    """
    Manages user interactions with the bot, including storing user data and processing messages.

    Attributes:
        bot (telebot.TeleBot): The bot instance.
        bot_message_broker (BotMessageBroker): An instance of the BotMessageBroker for sending messages.
        users_messages (dict): A dictionary storing UserMessageProcessor instances for each user.
        currencies (dict): A dictionary of available currencies with their values.
    """

    def __init__(self, bot, bot_message_broker):
        """
        Initialize the UserManager with bot, message broker, and default currencies.

        Args:
            bot (telebot.TeleBot): The bot instance.
            bot_message_broker (BotMessageBroker): The bot message broker instance.
        """
        self.bot = bot
        self.bot_message_broker = bot_message_broker

        self.users_messages = {}

        self.currencies = {
            'BTC': 63000,
            'USDC': 1
        }
    
    def add_new_user(self, message):
        """
        Add a new user to the users_messages dictionary with a UserMessageProcessor instance.

        Args:
            message (telebot.types.Message): The message object containing user details.
        """
        self.users_messages[message.chat.id] = UserMessageProcessor(
            self.bot, 
            self.bot_message_broker, 
            message.chat.id, 
            message.chat.username if message.chat.username != "None" and message.chat.username is not None else message.chat.first_name, 
            self.currencies
        )
    
    def set_start_message(self, message):
        """
        Set the start message data for the user.

        If the user does not exist, they are added first.

        Args:
            message (telebot.types.Message): The message object containing user details.
        """
        if message.chat.id in self.users_messages:
            self.users_messages[message.chat.id].set_start_message_data()
        else:
            self.add_new_user(message)
            self.users_messages[message.chat.id].set_start_message_data()
    
    def reply_user_message(self, message):
        """
        Generate a reply to the user's message.

        If the user does not exist, they are added first.

        Args:
            message (telebot.types.Message): The message object from the user.

        Returns:
            tuple: Arguments and keyword arguments for sending the reply message.
        """
        if message.chat.id in self.users_messages:
            return self.users_messages[message.chat.id].reply_message(message)
        self.add_new_user(message)
        return self.users_messages[message.chat.id].reply_message(message)

    def check_user_message(self, message=None):
        """
        Check the user's message for validity and process it accordingly.

        If the user does not exist, they are added first.

        Args:
            message (telebot.types.Message, optional): The message object from the user. Defaults to None.

        Returns:
            tuple: A tuple containing a boolean indicating the validity of the message, error message arguments, and keyword arguments.
        """
        if message.chat.id in self.users_messages:
            return self.users_messages[message.chat.id].check_message(message=message)
        self.add_new_user(message)
        return self.users_messages[message.chat.id].check_message(message=message)
    
    def on_update_currencies(self, currencies):
        """
        Update the available currencies for all users.

        Args:
            currencies (dict): A dictionary of available currencies with their values.
        """
        self.currencies = currencies
        for user in self.users_messages:
            self.users_messages[user].update_currencies(currencies)