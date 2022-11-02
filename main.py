import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

os.environ["TZ"] = "UTC+00:00"  # fix timezone


def init_logger(bot_slug: str):
    logger = logging.getLogger()

    # File logging
    logDir = Path(__file__).parent.parent.joinpath("logs")
    if not logDir.exists():
        os.makedirs(str(logDir.absolute()))
    # file_time = datetime.datetime.now().isoformat().replace(":", "-")[:19]
    logFilename = logDir.joinpath(bot_slug + ".log")
    print("Logging to file:", str(logFilename))
    # fileHandler = logging.FileHandler(filename=str(logFilename), encoding="utf-8")
    fileHandler = RotatingFileHandler(
        logFilename,
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=2,
        encoding="utf-8",
    )
    fileHandler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
    )
    logger.addHandler(fileHandler)

    # Screen stream logging
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
    )
    logger.addHandler(streamHandler)

    # Loggin Level
    # logger.setLevel(logging.WARNING)
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)

    return logger


from thebot import error_handler, message_handler
from thebot.my_bot import MyBot

# Initialize
slug = "mmbot"


bot = MyBot(
    slug=slug,
    mixin_config_file="../config/mixin.json",
    operation_config_file="../config/operation.json",
    message_handle=message_handler.handle,
    error_handle=error_handler.handle,
    logger=init_logger(slug),
)
bot.refresh_my_profile()
print("current bot:", bot.profile.user_id)
print(bot.profile.mixin_number, bot.profile.name)


# run blaze forever
bot.blaze.run_forever(3)
