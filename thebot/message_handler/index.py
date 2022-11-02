from mixinsdk.types.message import MESSAGE_CATEGORIES, MessageView

from thebot import cache
from thebot.my_bot import MyBot
from thebot.types import MM_ADDR_TYPES, MessageHandlerContext, MixinMessageUser

from . import handle_conversation_actions, handle_media, handle_text, handle_transfer


def handle(bot: MyBot, message):
    logger = bot.logger

    action = message["action"]

    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        # mixin bot.blaze server received the message
        return

    if action == "LIST_PENDING_MESSAGES":
        print("Mixin bot.blaze server: 👂")
        return

    if action == "ERROR":
        logger.warn("--- received error action ---")
        logger.warn(message)
        return
        """example message={
            "id": "00000000-0000-0000-0000-000000000000",
            "action": "ERROR",
            "error": {
                "status": 202,
                "code": 400,
                "description": "The request body can't be parsed as valid data.",
            },
        }"""

    if action == "CREATE_MESSAGE":
        error = message.get("error")
        if error:
            logger.warn("--- received error message ---")
            logger.warn(message)
            return

        # parse message
        msgview = MessageView.from_dict(message["data"])
        msgview.data_parsed = bot.blaze.parse_message_data(
            msgview.data, msgview.category
        )
        # print("\nmessage:", msgview.to_dict())

        if msgview.conversation_id == "":
            # is response status of send message, ignore
            return

        if msgview.type == "message":
            # From system message
            if msgview.user_id == "00000000-0000-0000-0000-000000000000":
                logger.debug("received system message")
                logger.debug(msgview.to_dict())

                if msgview.category == MESSAGE_CATEGORIES.SYSTEM_CONVERSATION:
                    handle_conversation_actions.handler(bot, msgview)

                    # reply to conversation (if have responding messages)
                    for msg in ctx.replying_msgs:
                        bot.blaze.send_message(msg)

                    bot.blaze.echo(msgview.message_id)
                    return

                logger.warn(f"unknown system message category: {msgview.category}")
                return

            # Ignore: MESSAGE_CATEGORIES.MESSAGE_RECALL
            if msgview.category == MESSAGE_CATEGORIES.MESSAGE_RECALL:
                logger.debug("received message recall, ignore it")
                bot.blaze.echo(msgview.message_id)
                return

            # Else: message from user

            # Init context.msguser
            msguser = MixinMessageUser()
            msguser.user_id = msgview.user_id
            msguser.user_type = cache.get_user_type_by_mixin_user_id(
                bot, msguser.user_id
            )
            (
                msguser.mm_addr_type,
                msguser.mm_addr_uid,
            ) = cache.get_user_addr_by_mixin_conversation(
                bot, msgview.conversation_id, msgview.user_id
            )
            msguser.is_in_group = msguser.mm_addr_type == MM_ADDR_TYPES.MIXIN_GROUP

            log = f"Message {msgview.message_id}, {msgview.category}"
            log += f"\n\tFrom: {msguser.user_type} - {msguser.user_id}"
            if msguser.is_in_group:
                log += f", In group: {msguser.conversation_id}"
            logger.info(log)

            ctx = MessageHandlerContext(msguser, msgview)

            if msgview.category == MESSAGE_CATEGORIES.SYSTEM_ACCOUNT_SNAPSHOT:
                try:
                    handle_transfer.handler(bot, ctx, msguser, msgview)
                    # reply to user (if have responding messages)
                    if msguser.mm_addr_type in [
                        MM_ADDR_TYPES.MIXIN_USER,
                        MM_ADDR_TYPES.MIXIN_GROUP,
                    ]:
                        for msg in ctx.replying_msgs:
                            bot.blaze.send_message(msg)
                    else:
                        logger.debug(
                            f"user addr type is {msguser.mm_addr_type}, so ignore to reply message"
                        )

                    bot.blaze.echo(msgview.message_id)
                except Exception as e:
                    logger.exception("at snapshot message", exc_info=True)
                    raise e from None
                return

            if msgview.category in [
                MESSAGE_CATEGORIES.PLAIN_TEXT,
                MESSAGE_CATEGORIES.ENCRYPTED_TEXT,
            ]:
                try:
                    handle_text.handler(bot, ctx, msguser, msgview)
                    # reply to user (if have responding messages)
                    for msg in ctx.replying_msgs:
                        bot.blaze.send_message(msg)
                    bot.blaze.echo(msgview.message_id)
                except Exception as e:
                    logger.exception("at text message", exc_info=True)
                    raise e from None
                return

            if msgview.category in [
                MESSAGE_CATEGORIES.PLAIN_POST,
                MESSAGE_CATEGORIES.ENCRYPTED_POST,
            ]:
                handle_post(bot.blaze, ctx, msguser, msgview)
                # reply to user (if have responding messages)
                for msg in ctx.replying_msgs:
                    bot.blaze.send_message(msg)
                bot.blaze.echo(msgview.message_id)
                return

            if msgview.category in [
                MESSAGE_CATEGORIES.PLAIN_IMAGE,
                MESSAGE_CATEGORIES.ENCRYPTED_IMAGE,
                MESSAGE_CATEGORIES.PLAIN_AUDIO,
                MESSAGE_CATEGORIES.ENCRYPTED_AUDIO,
                MESSAGE_CATEGORIES.PLAIN_VIDEO,
                MESSAGE_CATEGORIES.ENCRYPTED_VIDEO,
                MESSAGE_CATEGORIES.PLAIN_FILE,
                MESSAGE_CATEGORIES.ENCRYPTED_FILE,
                MESSAGE_CATEGORIES.PLAIN_STICKER,
                MESSAGE_CATEGORIES.ENCRYPTED_STICKER,
                MESSAGE_CATEGORIES.APP_CARD,
                MESSAGE_CATEGORIES.PLAIN_LIVE,
                MESSAGE_CATEGORIES.PLAIN_CONTACT,
                MESSAGE_CATEGORIES.ENCRYPTED_CONTACT,
            ]:

                try:
                    handle_media.handler(bot, ctx, msguser, msgview)
                    # reply to user (if have responding messages)
                    for msg in ctx.replying_msgs:
                        bot.blaze.send_message(msg)
                    bot.blaze.echo(msgview.message_id)
                except Exception as e:
                    logger.exception("at text message", exc_info=True)
                    raise e from None
                return

            msg = f"Unknown/Ignore message category: {message}"
            logger.warn(msg)
            bot.notify_operator_info(msg)
            bot.blaze.echo(msgview.message_id)
            return

    msg = f"Unknown message: {message}"
    logger.warn(msg)
    bot.notify_operator_info(msg)


def handle_post(
    bot: MyBot,
    ctx: MessageHandlerContext,
    msguser: MixinMessageUser,
    msgview: MessageView,
):
    pass
