import logging

from mixinsdk.types.message import MESSAGE_CATEGORIES, MessageView
from thebot.my_bot import MyBot
from thebot.types import MM_ADDR_TYPES, MessageHandlerContext, MixinMessageUser


def handler(
    bot: MyBot,
    ctx: MessageHandlerContext,
    msguser: MixinMessageUser,
    msgview: MessageView,
):

    # ----- 过滤消息
    #   过滤未知的用户类型
    if not msguser.user_type:
        logging.warn(f"Ignore unsupported user's message: {msgview.to_dict()}")
        return
    #   过滤来自机器人的消息。 不然机器人直接可能相互收发消息无止境
    if msguser.user_type == MM_ADDR_TYPES.MIXIN_APP:
        logging.info("Ignore mixin app user's message")
        return
    #   过滤群组中的所有 media 消息
    if msguser.is_in_group:
        logging.inf("Ignore all media message in group conversation")
        return

    bot.add_replying_text_message(ctx, "Handled", True)
