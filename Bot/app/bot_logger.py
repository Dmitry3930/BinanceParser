import logging

class BotLogger():
    """
    A logger class for the bot, providing various logging functionalities.

    Args:
        is_print (bool): Whether to also print log messages to the console. Default is False.
    """

    def __init__(self, is_print=False):
        """
        Initialize the BotLogger with logging configuration and message formats.

        Args:
            is_print (bool): Whether to also print log messages to the console. Default is False.
        """

        self.is_print = is_print

        self.logger = logging.getLogger('BOT')
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s [%(name)-3s] %(levelname)-4s: %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

        self.reply_types = {
            'start': 'start-reply',
            'help': 'help-reply',
            'text': 'text: {0}',
            'auto': 'auto-reply',

            'sending': 'reply: {0} Sending...',
            'sended': 'reply: {0} Sended!',

            'error sending': 'error reply: {0} Sending...',
            'error sended': 'error reply: {0} Sended!',

            'message': '{0}',
            'short_info': 'New short description: {0}',
            'long_info': 'New description: {0}'
        }

        self._log_string('Bot Inited!')

        self._log_string('')
    
    def _log_string(self, log_message):
        """
        Logs a message to the configured logger and optionally prints it.

        Args:
            log_message (str): The message to log.
        """
        self.logger.info(log_message)

        if self.is_print is True:
            print(log_message)
    
    def log(self, username, chat_id, reply_type, message_id=None, log_message=None):
        """
        Log a formatted message based on the type of reply and user information.

        Args:
            username (str): The username of the user.
            chat_id (int): The chat ID where the message was sent.
            reply_type (str): The type of reply being logged.
            message_id (str, optional): The ID of the message. Default is None.
            log_message (str, optional): The log message. Default is None.
        """
        message_id = f'[message_id: {message_id}] ' if message_id is not None else ''

        if reply_type != 'message':
            log_message = f'{message_id}user: "{username}" ({chat_id}), {self.reply_types[reply_type].format(repr(log_message)) if log_message is not None else ""}'
        else:
            log_message = f'{message_id}{self.reply_types[reply_type].format(repr(log_message)) if log_message is not None else ""}'

        self._log_string(log_message)
    
    def exit_message(self):
        """
        Log a message indicating that the bot is exiting.
        """
        self._log_string('Bot Exited!')
    
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
    
    def log_warning(self, warning_message):
        """
        Log a warning message.

        Args:
            warning_message (str): The warning message to log.
        """
        self._log_string(f'WARNING: "{warning_message}"')