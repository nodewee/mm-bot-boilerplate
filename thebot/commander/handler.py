from thebot.my_bot import MyBot
from thebot.types import MessageHandlerContext


def handle(
    bot: MyBot,
    ctx: MessageHandlerContext,
    msg_text: str,
):
    cmd = msg_text.lower()
    if cmd in ["hi", "hello"]:
        bot.add_replying_text_message(ctx, "Welcome!")
    elif cmd == "steve jobs":
        bot.add_replying_markdown_message(ctx, "**Stay hungry, stay foolish.**")
    else:
        bot.add_replying_text_message(ctx, "Unknown command", True)
