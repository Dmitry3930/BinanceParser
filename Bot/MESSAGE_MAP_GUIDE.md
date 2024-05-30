# Instructions for Creating a Message Map for the Bot
## Location of the Message Map
The message map is located in the script `app/user_message_processor.py` in the `update_message_map` method of the `UserMessageProcessor` class, in the `message_map` attribute.

---
## Main Points for Creating the Message Map
This message map has a recursive structure, with each subsequent message being nested inside the previous one.

Each message consists of the following attributes:
- `"bot_message"` - Contains the message that the bot should send. You can also add templates to the text.
- `"error_message"` - Contains the message the bot will send if the data is entered incorrectly. You can also add templates to the text.
- `"message_data"` - Contains the data that the bot will receive for further processing.
    - It can be of two types:
        - `message_data_key (str)` - The name of the key for the `message_data` attribute of the `UserMessageProcessor` class.
        - `list(message_data_key (str), template (dict))`:
            - `message_data_key (str)` - The name of the key for the `message_data` attribute of the `UserMessageProcessor` class.
            - `template (dict)` - An auto-replacement template, needed when the user enters some data and the bot needs to process it.
- `"message_action"` - Contains the action that the bot will perform upon reaching this message.
- `"type"` - Contains the validator class for the next message.
- `"reply_actions"` - Contains a dictionary where the keys are user actions according to the `"type"`, and the values are message maps.

---
## Description of `"type"`
Response types to messages are located in the script `app/reply_actions.py`.

These classes are responsible for checking user messages and generating responses to them.

### `BaseReplyAction`
The base class from which all classes for `"type"` are inherited.

This class is not used for message validation.

### `ErrorReplyAction: BaseReplyAction`
A class that exists as a placeholder in case the `"type"` was passed a class not inherited from `BaseReplyAction`, or directly `BaseReplyAction`.

It always returns an error message and is final, even if `"reply_actions"` are set for it.

### `ButtonReply: BaseReplyAction`
A class that defines the type of responses as buttons in Telegram, adds the `reply_markup` argument to the message.

If the message is not one of the keys in `"reply_actions"`, it will return the error message specified in `"error_message"`, otherwise, it will return the message specified in `"bot_message"`.

### `ValueReply: BaseReplyAction`
A class that defines the type of responses as a floating-point value.

If the message passes the parsing defined in the `_parse_value_str` method and still cannot be converted to `float`, it will return the error message specified in `"error_message"`, otherwise, it will return the message specified in `"bot_message"`.

#### `ValueReply._parse_value_str`
Replaces the comma with a dot, removes the dollar sign, then removes the space with the currency name, and finally removes all remaining spaces.

Returns the processed message.

### `EndReply: BaseReplyAction`
It is a closing message, after which the very first message from the highest level of the message map is always sent.

There are no validations for this type, it always considers the received message correct.

---
## Custom Validators
You can add your own message validation methods by examining the `BaseReplyAction` class and its methods.

### Class Attributes of `BaseReplyAction`
- `reply_actions (dict)` - Map of messages starting from the position `"reply_actions"` of this message.
- `templates_rules (dict)` - Dictionary of template replacement rules.
- `currencies (list)` - List of cryptocurrency names.
- `templates (dict)` - Dictionary of template replacements.

### `BaseReplyAction.__init__(self, reply_actions, templates_rules, currencies)`
Initializes the validator class.

Arguments:
- `reply_actions (dict)` - Map of messages starting from the position `"reply_actions"` of this message.
- `templates_rules (dict)` - Dictionary of template replacement rules.
- `currencies (list)` - List of cryptocurrency names.

### `BaseReplyAction.set_templates(self, value: str, coords: list)`
Sets the value for template replacements with the corresponding coordinate.

Arguments:
- `value (str)` - The value to replace the template with.
- `coords (list)` - The coordinate of the message map where the template replacement value will be set.

### `BaseReplyAction.check_reply_actions_is_none(self)`
Checks if the `reply_actions` attribute is `None`.

### `BaseReplyAction.try_get_message_coordinate(self, message_string)`
Attempts to obtain the coordinate of the message map for the next message.

This method is responsible for checking user messages.

Argument:
- `message_string (str)` - User message.

Returns:
- `tuple(is_valid (bool), reply_actions_key (string))`:
    - `is_valid (bool)` - Validation flag, if the message passes the check, the result will be `True`, otherwise: `False`.
    - `reply_actions_key (string|None)` - Key for the dictionary attribute `reply_actions`, is the coordinate of the next message in the message map, `None` if the user message is not valid.

### `BaseReplyAction.reply(self, bot, telegram_message, bot_message)`
Generates `*args` and `**kwargs` for the `bot.send_message` method.

Processes the final message using the `parse_templates` function from the `app/utils.py` script.

Arguments:
- `bot (telebot.TeleBot)` - `telebot` instance.
- `telegram_message (telebot.types.Message)` - Message object from `bot.message_handler`.
- `bot_message (str)` - Bot message from the message map.

Returns:
- `tuple(bot_message_handler_args (list(chat_id (str|int), parsed_message (str))), bot_message_handler_kwargs (dict), is_end (bool))`:
    - `bot_message_handler_args (list(chat_id (str|int), parsed_message (str)))` - `*args` for the `bot.send_message` method:
        - `chat_id (str|int)` - ID of the user who sent the message to the bot.
        - `parsed_message (str)` - Message from the message map, with all built-in templates replaced.
    - `bot_message_handler_kwargs (dict)` - `**kwargs` for the `bot.send_message` method.
        - More detailed information [here](https://pytba.readthedocs.io/en/latest/async_version/index.html#telebot.async_telebot.AsyncTeleBot.send_message).
    - `is_end (bool)` - Flag indicating the end of the message branch in the message map, if `True`, then the start message will be generated immediately after this message.

### `BaseReplyAction.reply_error(self, bot, telegram_message, bot_error_message, error_result=None, exception=Exception("exception_text"))`
Generates `*args` and `**kwargs` for the `bot.send_message` method.

Replaces standard templates:
- `<error_value>` -> `error_result` if `error_result` exists
- `<true_result>` -> `self.reply_actions`
- `<exception>` -> `exception` if `exception` is an instance of the `Exception` class

Processes the final message using the `parse_templates` function from the `app/utils.py` script.

Arguments:
- `bot (telebot.TeleBot)` - `telebot` instance.
- `telegram_message (telebot.types.Message)` - Message object from `bot.message_handler`.
- `bot_error_message (str)` - Bot error message from the message map.
- `error_result (str, optional)` - Error message text. Defaults to `None`.
- `exception (Exception, optional)` - Bot `exception` message.

Returns:
- `tuple(bot_message_handler_args (list(chat_id (str|int), parsed_message (str))), bot_message_handler_kwargs (dict))`:
    - `bot_message_handler_args (list(chat_id (str|int), parsed_message (str)))` - `*args` for the `bot.send_message` method:
        - `chat_id (str|int)` - ID of the user who sent the message to the bot.
        - `parsed_message (str)` - Message from the message map, with all built-in templates replaced.
    - `bot_message_handler_kwargs (dict)` - `**kwargs` for the `bot.send_message` method.
        - More detailed information [here](https://pytba.readthedocs.io/en/latest/async_version/index.html#telebot.async_telebot.AsyncTeleBot.send_message).

### `BaseReplyAction.get_data(self, message, template=None)`
Gets data from the message.

If a template replacement is specified, `message` becomes the key for that template, then it returns `template[message]`.

If no template replacement is specified, it returns `message`.

Template replacement is necessary to convert a specific string to the required format, as shown here:
```python
>> message = "When it exceeds"
>> template = {"When it exceeds": True, "When it is below": False, "When it crosses": None}
>>
>> reply_action = BaseReplyAction(...)
>>
>> reply_action.get_data(message, template=template)
True
>> reply_action.get_data(message)
"When it exceeds"
```

Arguments:
- `message (str)` - User message text.
- `template (dict, optional)` - Template replacement. Defaults to `None`.

Returns:
- `message_data (Any)` - Data from the `message` or the `message` itself.

---

### Пример реализации кастомного валидатора
```python
from datetime import datetime

class DatetimeReply(BaseReplyAction):
    """
    Example of a simple class for handling datetime type messages.
    """

    def __init__(self, reply_actions, templates_rules, currencies) -> None:
        """
        Here, besides the main attributes, an attribute 
        datetime_format was added, responsible for the parsing format of the string into datetime.
        """
        super().__init__(reply_actions, templates_rules, currencies)
        self.datetime_format = '%m/%d/%y %H:%M:%S'

    def _parse_datetime(self, message_string):
        """
        This private method parses the string into datetime format.

        Argument:
            message_string (str): User message.

        Returns:
            message_datetime (datetime.datetime): Datetime from the message.
        """
        return datetime.strptime(message_string, '%m/%d/%y %H:%M:%S')

    def try_get_message_coordinate(self, message_string):
        """
       In this case, we defined that for messages of this type, 
        there is only one possible response and we set its coordinate as "".
        So in this case, the method simply checks the validity of the message using a "try-except" block.
        """
        try:
            message_value = self._parse_datetime(message_string)
            return True, ""
        except Exception:
            return False, ""

    def reply(self, bot, telegram_message, bot_message):
        """
        Standard reply, except for the addition of an argument responsible for removing 
        the Telegram keyboard buttons. Also, it is specified here that this type of message 
        does not close the branch, therefore subsequent messages can follow it.
        """
        return [telegram_message.chat.id, parse_templates(bot_message, **self.templates)], {'reply_markup': types.ReplyKeyboardRemove()}, False

    def get_data(self, message, template=None):
        """
        This method implements data retrieval from the message. 
        It is worth noting that a "try-except" block is not needed here, 
        as the check has already been implemented in the "try_get_message_coordinate" method.

        Returns:
            message_datetime (datetime.datetime): Datetime from the message.
        """
        return self._parse_datetime(message)
```

---
## Templates
### Common Rules for Creating Templates
In addition to the capabilities of formatted strings, templates for messages sent by the bot have also been added.

Essentially, a template is a rule for replacing specific text in tag format with specific messages or data obtained during the processing of messages by the bot.

The templates themselves can be added directly into the bot's message text inside a tag, like this:
```python
...
"bot_message": "Хорошо <user>, в следующем сообщении будет темплейт числа, введите любое число"
...
```

There are also special templates for error messages, which do not need to be set through the `message_templates` rules. These are the following templates:
- `error_value` - This template is replaced by the user's message.
- `true_result` - This template is set inside the subclass `BaseReplyAction` in the method `reply_error`.

It's also necessary to establish rules for templates, which is done in the dictionary attribute `message_templates` of the class `UserMessageProcessor`.

To do this, you need to specify the template name, the data it will be replaced with (default is `None` if the replacement is expected later), and the message's ordinal number or coordinates (set to `None` if no coordinate is specified for replacement).

```python
self.message_templates = {
    "user": [None, 1] # Will be replaced after the first user message
    "number": [None, 2], # Will be replaced after the second user message
    "some_text": ["Irreplaceable text", None], # Will be replaced when encountered
}
```

### Example of Working with Templates
Let's assume the message map looks like this:
```python
self.message_map = {
    "bot_message": "Hello <user>, this is an example bot conversation, what's your name? <some_text>",
    "error_message": "I can't respond to '<error_value>', but I can respond based on the following rules:\n<true_result>",
    "message_data": None,
    "message_action": None,
    "type": TextReply,
    "reply_actions": {
        "": {
            "bot_message": "Alright <user>, the next message will contain a template for a number, please enter any number",
            "error_message": "I can't respond to '<error_value>', but I can respond based on the following rules:\n<true_result>",
            "message_data": "user_name",
            "message_action": None,
            "type": NumberReply,
            "reply_actions": {
                "": {
                    "bot_message": "<user>, you entered <number>. <some_text>",
                    "error_message": "I can't respond to '<error_value>', but I can respond based on the following rules:\n<true_result>",
                    "message_data": "user_value",
                    "message_action": None,
                    "type": EndReply,
                    "reply_actions": None
                }
            }
        }
    }
}

...

self.message_templates = {
    "user": [None, 1] # Will be replaced after the first user message
    "number": [None, 2], # Will be replaced after the second user message
    "some_text": ["Irreplaceable text", None], # Will be replaced when encountered
}
```

The conversation will proceed as follows:

- **Bot**: Hello , this is an example bot conversation, what's your name? `Irreplaceable text`

- **You**: `Mike`

- **Bot**: Alright `Mike`, the next message will contain a template for a number, please enter any number

- **You**: `A`

- **Bot**: I can't respond to '`A`', but I can respond based on the following rules:
- **Bot**: The message must be a number.

- **You**: `1`

- **Bot**: `Mike`, you entered `1`. `Незаменимый текст`

- **Bot**: Hello `Mike`, this is an example bot conversation, what's your name? `Irreplaceable text`

---
## Conclusions
These are all the rules for creating a message map. While they may seem somewhat cumbersome, they provide a high level of flexibility when creating message branches.

## Potential Improvements
- Localization for different languages could be added here as well.
- In some cases, it might also be possible to add images. Though when implementing a validator, adding images, even generated ones, could be possible if needed.
- Perhaps the data autoreplacement template should be updated to make it more flexible than a simple dictionary replacement.