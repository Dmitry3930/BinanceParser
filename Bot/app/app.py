from telebot.async_telebot import AsyncTeleBot
from telebot.util import smart_split
from bot_message_broker import BotMessageBroker
from users_manager import UserManager
from utils import get_message_id
from currencies_to_str import set_currencies_to_str, CURRENCIES2STR_SHORT, CURRENCIES2STR_LONG, CURRENCIES2STR_FULL
from bot_logger import BotLogger
from time import time

import argparse
import asyncio

# Parsing command-line arguments to get the bot token
args_parser = argparse.ArgumentParser()
args_parser.add_argument('--token', help='Telegram Bot Token')
args = args_parser.parse_args()


# Initializing the Telegram bot with the provided token
bot = AsyncTeleBot(args.token)
del args

# Initializing logging, message broker, and user manager
bot_docker_logger = BotLogger()
bot_message_broker = BotMessageBroker()
message_processor = UserManager(bot, bot_message_broker)

async def try_except_send_message(username, message_id, *message_args, **message_kwargs):
    """
    Attempts to send a message with retries in case of failure.

    Args:
        username (str): Username of the message recipient.
        message_id (str): Unique ID of the message.
        message_args (tuple): Positional arguments for the message.
        message_kwargs (dict): Keyword arguments for the message.
    """
    max_retries = 10
    retry_number = 0

    while retry_number < max_retries:
        try:
            if retry_number > 0:
                bot_docker_logger.log_info(
                    f'A bot problem was solved after {retry_number+1} attempts!'
                )

            await bot.send_message(*message_args, **message_kwargs)
            return
        except Exception as exception:
            retry_message = 'Retrying...'
            if retry_number >= max_retries-1:
                retry_message = f'A bot could not resolve the problem after {max_retries} attempts. Message skipped!'

            bot_docker_logger.log_exception(
                f'The bot tried to send a message, but it encountered the following problem: "{exception}". ' \
                f'What it tried to send: "{message_args}", "{message_kwargs}". User data: {username}. Message ID: {message_id}. ' \
                f'Retry number: {retry_number+1}/{max_retries}. {retry_message}'
            )
            retry_number += 1


async def try_send_message(username, message_id, *message_args, **message_kwargs):
    """
    Tries to send a message and handles long messages by splitting them if necessary.

    Args:
        username (str): Username of the message recipient.
        message_id (str): Unique ID of the message.
        message_args (tuple): Positional arguments for the message.
        message_kwargs (dict): Keyword arguments for the message.
    """
    if isinstance(message_args[1], str) is False:
        bot_docker_logger.log_exception(
            f'Bot message must be a "str" type, not: "{type(message_args[1])}". ' \
            f'Excepted message: "{message_args[1]}". User data: {username} ({message_args[0]}). Message ID: {message_id}.'
        )
        return
    
    if len(message_args[1]) > 4096:
        bot_docker_logger.log_warning(
            f'Bot message length must be lower than 4096 characters, but you try to send {len(message_args[1])} characters. ' \
            f'Excepted message: "{message_args[1]}". User data: {username} ({message_args[0]}). Message ID: {message_id}.'
        )

        messages = smart_split(message_args[1])

        for message in messages:
            log_and_send_message(username, message_id, *message_args, **message_kwargs)
        return
    
    await try_except_send_message(username, message_id, *message_args, **message_kwargs)


async def log_and_send_message(username, message_id, *message_args, **message_kwargs):
    """
    Logs the sending process and sends a message.

    Args:
        username (str): Username of the message recipient.
        message_id (str): Unique ID of the message.
        message_args (tuple): Positional arguments for the message.
        message_kwargs (dict): Keyword arguments for the message.
    """
    bot_docker_logger.log(username, message_args[0], 'sending', message_id=message_id, log_message=message_args[1])
    await try_except_send_message(username, message_id, *message_args, **message_kwargs)
    bot_docker_logger.log(username, message_args[0], 'sended', message_id=message_id, log_message=message_args[1])


async def log_and_try_send_message(username, message_id, *message_args, **message_kwargs):
    """
    Logs the sending process and tries to send a message.

    Args:
        username (str): Username of the message recipient.
        message_id (str): Unique ID of the message.
        message_args (tuple): Positional arguments for the message.
        message_kwargs (dict): Keyword arguments for the message.
    """
    bot_docker_logger.log(username, message_args[0], 'sending', message_id=message_id, log_message=message_args[1])
    await try_send_message(username, message_id, *message_args, **message_kwargs)
    bot_docker_logger.log(username, message_args[0], 'sended', message_id=message_id, log_message=message_args[1])


async def log_and_try_reply_message(username, message, message_id):
    """
    Logs the process and tries to reply to a user message.

    Args:
        username (str): Username of the message sender.
        message (object): Telegram message object.
        message_id (str): Unique ID of the message.
    """
    message_args, message_kwargs, is_end = message_processor.reply_user_message(message)
    await log_and_try_send_message(username, message_id, *message_args, **message_kwargs)
    return is_end


def log_end_message(username, chat_id, message_id, log_message):
    """
    Logs the end of a message processing sequence.

    Args:
        username (str): Username of the message sender.
        chat_id (int): Chat ID of the message.
        message_id (str): Unique ID of the message.
        log_message (str): Log message content.
    """
    bot_docker_logger.log(username, chat_id, 'message', message_id=message_id, log_message=log_message)
    bot_docker_logger.log(username, chat_id, 'message', message_id=message_id)



@bot.message_handler(commands=['start'])
async def start(message):
    """
    Handles the /start command by sending a welcome message and replying to the user.

    Args:
        message (object): Telegram message object.
    """
    message_id = get_message_id()

    username = message.chat.username if message.chat.username != "None" and message.chat.username is not None else message.chat.first_name
    bot_docker_logger.log(username, message.chat.id, 'start', message_id=message_id)
    message_processor.set_start_message(message)

    bot_message = "Hello, I am a test bot for price notifications on Binance"
    await log_and_try_send_message(username, message_id, message.chat.id, bot_message)

    await log_and_try_reply_message(username, message, message_id)

    log_end_message(username, message.chat.id, message_id, 'message replied!')


@bot.message_handler(commands=['help'])
async def help(message):
    """
    Handles the /help command by sending /help message and replying to the user.

    Args:
        message (object): Telegram message object.
    """
    message_id = get_message_id()

    username = message.chat.username if message.chat.username != "None" and message.chat.username is not None else message.chat.first_name

    bot_docker_logger.log(username, message.chat.id, 'help', message_id=message_id)

    bot_help_messages = [
        f'Hello, I am a test bot for price notifications on Binance',
        f'I can show the current exchange rate of the cryptocurrencies you specify, and I can also notify you if a cryptocurrency pair reaches the desired value',
        set_currencies_to_str(message_processor.currencies, mode=CURRENCIES2STR_FULL)
    ]

    for bot_help_message in bot_help_messages:
        await log_and_try_send_message(username, message_id, message.chat.id, bot_help_message, parse_mode='HTML')

    await log_and_try_reply_message(username, message, message_id)
    
    log_end_message(username, message.chat.id, message_id, 'message replied!')


@bot.message_handler(content_types=['text'])
async def set_data(message):
    """
    Handles text messages, checks them, and responds accordingly.

    Args:
        message (object): Telegram message object.
    """
    message_id = get_message_id()

    username = message.chat.username if message.chat.username != "None" and message.chat.username is not None else message.chat.first_name
    bot_docker_logger.log(username, message.chat.id, 'text', message_id=message_id, log_message=message.text)
    check_result, error_message_args, error_message_kwargs = message_processor.check_user_message(message)
    if check_result is False:
        await log_and_try_send_message(username, message_id, *error_message_args, **error_message_kwargs)
    else:
        is_end = await log_and_try_reply_message(username, message, message_id)

        if is_end is True:
            message_processor.set_start_message(message)

            await log_and_try_reply_message(username, message, message_id)

    log_end_message(username, message.chat.id, message_id, 'message replied!')
    

async def notify(bot, message):
    """
    Sends notifications about currency price updates.

    Args:
        bot (AsyncTeleBot): The Telegram bot instance.
        message (dict): Notification message details.
    """
    message_id = get_message_id()

    bot_docker_logger.log(message["user"][1], message, 'auto', message_id=message_id)

    notify_message =    f'{message["user"][1]}, {message["pair1_name"]} has become {"greater" if message["condition_flag"] is True else "less"} than ' \
                        f'{message["check_value"]} {message["pair2_name"]} and is now {message["now_pair_value"]} {message["pair2_name"]}'

    await log_and_try_send_message(message["user"][1], message_id, message["user"][0], notify_message)

    log_end_message(message["user"][1], message["user"][0], message_id, 'auto-reply sended!')


class OnUpdateCurrencies():
    """
    Class to handle updates of currency rates.
    
    Attributes:
        req_time (float): Time of the last request.
        update_interval (float): Interval between updates in seconds.
    """

    def __init__(self, update_interval=60.0):
        """
        Initialize the OnUpdateCurrencies class.

        Args:
            update_interval (float): Interval in seconds for updates. Default is 60 seconds.
        """
        self.req_time = 0.0
        self.update_interval = update_interval
    
    async def __call__(self, bot: AsyncTeleBot, currencies):
        """
        Updates currency rates and logs the updates.

        Args:
            bot (AsyncTeleBot): The Telegram bot instance.
            currencies (list): List of updated currencies.
        """
        message_id = get_message_id()

        message_processor.on_update_currencies(currencies)
        if time() > self.req_time + self.update_interval:
            short_currencies_str = set_currencies_to_str(currencies, mode=CURRENCIES2STR_SHORT)
            long_currencies_str = set_currencies_to_str(currencies, CURRENCIES2STR_LONG)

            bot_docker_logger.log('ADMIN', 'SELF', 'short_info', message_id=message_id, log_message=short_currencies_str)

            await bot.set_my_short_description(short_currencies_str, 'ru')
            print(long_currencies_str)
            await bot.set_my_description(long_currencies_str, 'ru')

            self.req_time = time()

on_update_currencies = OnUpdateCurrencies()

async def check_messages():
    """
    Continuously checks for new messages from the message broker.
    """
    while True:
        await bot_message_broker.read_message_from_parser2bot_queue(notify, bot)
        await bot_message_broker.read_message_from_parser_info_queue(on_update_currencies, bot)
        await asyncio.sleep(1)


async def main():
    """
    Main entry point for running the bot and checking messages concurrently.
    """
    L = await asyncio.gather(
        bot.polling(),
        check_messages(),
    )
    bot_docker_logger.exit_message()

# Run the main function to start the bot
asyncio.run(main())