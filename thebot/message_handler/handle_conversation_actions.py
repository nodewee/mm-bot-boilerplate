from mixinsdk.types.message import MessageView

from thebot.my_bot import MyBot
from thebot.types import MM_ADDR_TYPES, MessageHandlerContext, MixinMessageUser


def handler(bot: MyBot, msgview: MessageView):
    logger = bot.logger

    participant_id = msgview.data_parsed.get("participant_id")
    if participant_id != bot.blaze.config.client_id:
        # Ignore actions that are not intended for this robot
        return
    msguser = MixinMessageUser()
    msguser.is_in_group = True
    msguser.mm_addr_type = MM_ADDR_TYPES.MIXIN_GROUP
    msguser.mm_addr_uid = msgview.conversation_id
    bot.get_mixin_group_profile(msguser, msgview.conversation_id)

    action = msgview.data_parsed.get("action")
    ctx = MessageHandlerContext(msguser, msgview)

    if action == "ADD":
        log = f"Joined group: {msgview.conversation_id}"
        logger.info(log)
        bot.add_replying_text_message(ctx, "Hello everyone!")
    elif action == "REMOVE":
        log = f"Left group: {msgview.conversation_id}"
        logger.info(log)
    else:
        logger.warn(f"Unknown conversation action: {action}")
