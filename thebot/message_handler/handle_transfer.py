from mixinsdk.clients.client_blaze import BlazeClient
from mixinsdk.types.message import MessageView

from thebot.my_bot import MyBot
from thebot.types import MessageHandlerContext, MixinMessageUser


def handler(
    bot: MyBot,
    ctx: MessageHandlerContext,
    msguser: MixinMessageUser,
    msgview: MessageView,
):
    logger = bot.logger
    logger.info(f"Received transfer data: {msgview.data_parsed}")
    bot.add_replying_text_message(ctx, "Handled", True)
