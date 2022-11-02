from thebot.my_bot import MyBot
from thebot.types import MessageHandlerContext


def handler(bot: MyBot, ctx: MessageHandlerContext):
    logger = bot.logger
    logger.info(f"Received transfer data: {ctx.msgview.data_parsed}")
    bot.add_replying_text_message(ctx, "Handled", True)
