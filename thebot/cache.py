from memoization import cached

from thebot.my_bot import MyBot


def custom_key_maker_1(_, mixin_user_id):
    return mixin_user_id


@cached(max_size=100, custom_key_maker=custom_key_maker_1)
def get_user_type_by_mixin_user_id(bot: MyBot, mixin_user_id: str):
    return bot.get_user_type_by_mixin_user_id(mixin_user_id)


def custom_key_maker_2(bot, conversation_id, mixin_user_id):
    return f"{conversation_id}_{mixin_user_id}"


@cached(max_size=100, custom_key_maker=custom_key_maker_2)
def get_user_addr_by_mixin_conversation(bot: MyBot, conversation_id, mixin_user_id):
    return bot.get_user_addr_by_mixin_conversation(conversation_id, mixin_user_id)
