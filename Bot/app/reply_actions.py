from telebot import types
from utils import parse_templates

class BaseReplyAction():
    """
    A base class for handling reply actions in a Telegram bot.

    Attributes:
        reply_actions (dict): A dictionary of reply actions.
        templates_rules (dict): A dictionary of template rules.
        currencies (list): A list of supported currencies.
        templates (dict): A dictionary of templates.
    """

    def __init__(self, reply_actions, templates_rules, currencies) -> None:
        """
        Initialize the BaseReplyAction with reply actions, template rules, and currencies.

        Args:
            reply_actions (dict): A dictionary of reply actions.
            templates_rules (dict): A dictionary of template rules.
            currencies (list): A list of supported currencies.
        """
        self.templates_rules = templates_rules
        self.templates = {}
        self.currencies = currencies

        self.reply_actions = reply_actions

    def set_templates(self, value: str, coords: list):
        """
        Set the templates based on the provided value and coordinates.

        Args:
            value (str): The value to set in the templates.
            coords (list): The coordinates to match against the template rules.
        """
        for template_rule_name in self.templates_rules:
            if self.templates_rules[template_rule_name][0] is not None:
                self.templates[template_rule_name] = self.templates_rules[template_rule_name][0]
            if self.templates_rules[template_rule_name][1] == coords or self.templates_rules[template_rule_name][1] == len(coords):
                self.templates[template_rule_name] = value

    def check_reply_actions_is_none(self):
        """
        Check if the reply actions are None.

        Returns:
            bool: True if reply actions are None, False otherwise.
        """
        return self.reply_actions is None
    
    def try_get_message_coordinate(self, message_string):
        """
        Attempt to get the message coordinate.

        Arg:
            message_string (str): The message string to check.

        Returns:
            tuple: A tuple containing a boolean indicating success and the coordinate (None in this case).
        """
        return True, None

    def reply(self, bot, telegram_message, bot_message):
        """
        Handle the reply action.

        Args:
            bot (telebot.TeleBot): The bot instance.
            telegram_message (telebot.types.Message): The incoming Telegram message.
            bot_message (str): The bot's reply message.

        Returns:
            tuple: A tuple containing the message arguments, message kwargs, and a boolean indicating completion.
        """
        return [], {}, False

    def reply_error(self, bot, telegram_message, bot_error_message, error_result=None, exception=Exception("Программа отработала корректно, видимо разработчик что-то не учёл")):
        """
        Handle an error reply action.

        Args:
            bot (telebot.TeleBot): The bot instance.
            telegram_message (telebot.types.Message): The incoming Telegram message.
            bot_error_message (str): The error message to send.
            error_result (str, optional): The error result to include in the template. Defaults to None.
            exception (Exception, optional): The exception that occurred. Defaults to a generic exception.

        Returns:
            tuple: A tuple containing the message arguments and message kwargs.
        """
        if error_result is not None:
            self.templates['error_value'] = error_result
        self.templates['true_result'] = self.reply_actions
        if isinstance(exception, Exception):
            self.templates['exception'] = exception
        return [telegram_message.chat.id, parse_templates(bot_error_message, **self.templates)], {}
    
    def get_data(self, message, template=None):
        """
        Get data from the message based on the template.

        Args:
            message (str): The message to process.
            template (dict, optional): The template to use for processing. Defaults to None.

        Returns:
            str: The processed message.
        """
        if template is None:
            return message
        return template[message]

class ButtonReply(BaseReplyAction):
    """
    A class for handling button reply actions in a Telegram bot.
    """

    def try_get_message_coordinate(self, message_string):
        """
        Attempt to get the message coordinate based on button actions.

        Args:
            message_string (str): The message string to check.

        Returns:
            tuple: A tuple containing a boolean indicating if the action exists and the message string.
        """
        return message_string in self.reply_actions, message_string
    
    def reply_error(self, bot, telegram_message, bot_error_message, error_result=None, exception=Exception("Программа отработала корректно, видимо разработчик что-то не учёл")):
        """
        Handle an error reply action with buttons.

        Args:
            bot (telebot.TeleBot): The bot instance.
            telegram_message (telebot.types.Message): The incoming Telegram message.
            bot_error_message (str): The error message to send.
            error_result (str, optional): The error result to include in the template. Defaults to None.
            exception (Exception, optional): The exception that occurred. Defaults to a generic exception.

        Returns:
            tuple: A tuple containing the message arguments and message kwargs with button markup.
        """
        telegram_message_args, telegram_message_kwargs = super().reply_error(bot, telegram_message, bot_error_message, error_result=error_result, exception=exception)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [button_text for button_text in self.reply_actions]
        markup.add(*buttons)
        return telegram_message_args, {'reply_markup': markup, **telegram_message_kwargs}
    
    def reply(self, bot, telegram_message, bot_message):
        """
        Handle the reply action with buttons.

        Args:
            bot (telebot.TeleBot): The bot instance.
            telegram_message (telebot.types.Message): The incoming Telegram message.
            bot_message (str): The bot's reply message.

        Returns:
            tuple: A tuple containing the message arguments, message kwargs with button markup, and a boolean indicating completion.
        """
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [button_text for button_text in self.reply_actions]
        markup.add(*buttons)
        return [telegram_message.chat.id, parse_templates(bot_message, **self.templates)], {'reply_markup': markup}, False

class ValueReply(BaseReplyAction):
    """
    A class for handling value-based reply actions in a Telegram bot.

    Attributes:
        max_value (int): The maximum allowed value for a message.
    """

    def __init__(self, reply_actions, templates_rules, currencies) -> None:
        """
        Initialize the ValueReply with reply actions, template rules, and currencies.

        Args:
            reply_actions (dict): A dictionary of reply actions.
            templates_rules (dict): A dictionary of template rules.
            currencies (list): A list of supported currencies.
        """
        super().__init__(reply_actions, templates_rules, currencies)
        self.max_value = 1000000000000000000

    def _parse_value_str(self, str_value):
        """
        Parse a string value, removing unnecessary characters.

        Args:
            str_value (str): The string value to parse.

        Returns:
            str: The cleaned string value.
        """
        parsed_string = str_value.replace(',', '.').replace('$', '')

        for currency in self.currencies:
            if f' {currency}' in parsed_string:
                str_value.replace(currency, '')
                break
        return parsed_string.replace(' ', '')

    def try_get_message_coordinate(self, message_string):
        """
        Attempt to get the message coordinate based on value.

        Args:
            message_string (str): The message string to check.

        Returns:
            tuple: A tuple containing a boolean indicating if the value is valid and an empty string.
        """
        message_string = self._parse_value_str(message_string)
        try:
            message_value = float(message_string)
            return message_value >= 0 and message_value <= self.max_value, ""
        except ValueError:
            return False, ""
    
    def reply(self, bot, telegram_message, bot_message):
        """
        Handle the reply action with value-based input.

        Args:
            bot (telebot.TeleBot): The bot instance.
            telegram_message (telebot.types.Message): The incoming Telegram message.
            bot_message (str): The bot's reply message.

        Returns:
            tuple: A tuple containing the message arguments, message kwargs without button markup, and a boolean indicating completion.
        """
        return [telegram_message.chat.id, parse_templates(bot_message, **self.templates)], {'reply_markup': types.ReplyKeyboardRemove()}, False
    
    def get_data(self, message, template=None):
        """
        Get data from the message based on value.

        Args:
            message (str): The message to process.
            template (dict, optional): The template to use for processing. Defaults to None.

        Returns:
            float: The processed message value as a float.
        """
        return float(self._parse_value_str(message))

class EndReply(BaseReplyAction):
    """
    A class for handling end reply actions in a Telegram bot.
    """

    def reply(self, bot, telegram_message, bot_message):
        """
        Handle the end reply action.

        Args:
            bot (telebot.TeleBot): The bot instance.
            telegram_message (telebot.types.Message): The incoming Telegram message.
            bot_message (str): The bot's reply message.

        Returns:
            tuple: A tuple containing the message arguments, message kwargs, and a boolean indicating completion.
        """
        return [telegram_message.chat.id, parse_templates(bot_message, **self.templates)], {}, True

class ErrorReplyAction(BaseReplyAction):
    def reply(self, bot, telegram_message, bot_message):
        return [telegram_message.chat.id, 'Карта сообщений задана ошибочно для данного сообщения, сообщите об ошибке разработчику'], {}, True