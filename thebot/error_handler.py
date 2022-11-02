from thebot.my_bot import MyBot


def handle(bot: MyBot, error):
    bot.logger.error(error, exc_info=True)
