import logging

from mixinsdk.clients.client_blaze import BlazeClient
from mixinsdk.clients.client_http import HttpClient_WithAppConfig
from mixinsdk.clients.client_http_nosign import HttpClient_WithoutAuth
from mixinsdk.clients.config import AppConfig
from mixinsdk.types.message import (
    pack_button,
    pack_button_group_data,
    pack_livecard_data,
    pack_message,
    pack_post_data,
    pack_text_data,
)
from mixinsdk.types.user import UserProfile as MixinUserProfile
from mixinsdk.utils import is_group_conversation

from .types import (
    MM_ADDR_TYPES,
    MessageHandlerContext,
    MixinMessageUser,
    OperationObject,
)


class MyBot:
    def __init__(
        self,
        mixin_config_file: str,
        operation_config_file: str,
        slug: str = "bot",
        message_handle: callable = None,
        error_handle: callable = None,
        logger: logging.Logger = None,
    ):

        self.config = AppConfig.from_file(mixin_config_file)
        self.noauth = HttpClient_WithoutAuth()
        self.http = HttpClient_WithAppConfig(self.config)
        self.logger = logger if logger else logging.getLogger("my-bot")

        def _blaze_on_message(blaze, message):
            message_handle(self, message)

        def _blaze_on_error(blaze, error):
            error_handle(self, error)

        self.blaze = BlazeClient(
            self.config,
            on_message=_blaze_on_message,
            on_error=_blaze_on_error,
        )

        self.slug: str = slug
        self.operation: OperationObject = OperationObject.from_file(
            operation_config_file
        )
        self.profile: MixinUserProfile = None

    def refresh_my_profile(self):
        r = self.http.api.user.get_me()
        data = r.get("data")
        if not data:
            return

        is_app = True if data.get("app", {}).get("type") == "app" else False
        self.profile = MixinUserProfile(
            user_id=data["user_id"],
            mixin_number=data["identity_number"],
            name=data["full_name"],
            avatar_url=data["avatar_url"],
            is_app=is_app,
        )
        self.blaze.profile = self.profile

    def get_mixin_group_profile(self, ctx_msguser: MixinMessageUser, group_conv_id):
        """no return. assign to ctx_msguser"""

        r = self.http.api.conversation.read(group_conv_id)
        if not isinstance(r, dict):
            raise ConnectionError(f"Cannot get group profile: {group_conv_id}")
        data = r.get("data")
        if not data:
            raise ConnectionError(f"Cannot get group profile: {group_conv_id}")
        if data.get("category") != "GROUP":
            raise ValueError(f"Not a group conversation: {group_conv_id}")
        group_name = data.get("name")
        participants = data.get("participants")
        group_admin_user_id_list = []
        for item in participants:
            role = item["role"].upper()
            user_id = item["user_id"]
            if role == "OWNER":
                group_owner_user_id = user_id
                group_admin_user_id_list.append(user_id)
                continue
            if role == "ADMIN":
                group_admin_user_id_list.append(user_id)

        ctx_msguser.group_name = group_name
        ctx_msguser.group_owner_user_id = group_owner_user_id
        ctx_msguser.group_admin_user_id_list = group_admin_user_id_list

    def get_user_type_by_mixin_user_id(self, mixin_user_id):
        # request mixin user info to known mm_addr_type and mm_addr_uid
        r = self.http.api.user.get_user(mixin_user_id)
        data = r.get("data", {})
        identity_number = data.get("identity_number")
        app = data.get("app")
        if not identity_number:
            addr_type = None
        elif identity_number == "0":  # Network user
            addr_type = None  # Unsupported
        # elif identity_number.startswith("7000"):  # Mixin App
        elif app:
            addr_type = MM_ADDR_TYPES.MIXIN_APP
        else:
            addr_type = MM_ADDR_TYPES.MIXIN_USER
        return addr_type

    def get_user_addr_by_mixin_conversation(self, mixin_conv_id, mixin_user_id):
        """return (mm_addr_type, mm_addr_uid)"""
        if not mixin_conv_id or not mixin_user_id:
            raise ValueError("Invalid mixin_conv_id or mixin_user_id")

        if is_group_conversation(mixin_conv_id, mixin_user_id, self.config.client_id):
            mm_addr = (MM_ADDR_TYPES.MIXIN_GROUP, mixin_conv_id)

            return mm_addr
        else:  # MIXIN APP or USER,
            addr_type = self.get_user_type_by_mixin_user_id(mixin_user_id)
            mm_addr = (addr_type, mixin_user_id)

            return mm_addr

    def send_text_message(self, text, conversation_id, quote_message_id=None):
        self.blaze.send_message(
            pack_message(
                pack_text_data(text), conversation_id, quote_message_id=quote_message_id
            )
        )

    def send_markdown_message(self, text, conversation_id, quote_message_id=None):
        self.blaze.send_message(
            pack_message(
                pack_post_data(text), conversation_id, quote_message_id=quote_message_id
            )
        )

    def send_button_group_message(
        self, buttons, conversation_id, quote_message_id=None
    ):
        self.blaze.send_message(
            pack_message(
                pack_button_group_data(buttons),
                conversation_id,
                quote_message_id=quote_message_id,
            )
        )

    def notify_operator_error(self, *args: str):
        text = "\n".join(list(args))
        self.logger.warn(f"notice operator error: {text}")
        text = f"{self.slug}:\n```\n" + text + "\n```"
        msg = pack_message(pack_post_data(text), self.operation.notice_error_conv_id)
        self.blaze.send_message(msg)

    def notify_operator_info(self, *args: str):
        text = "\n".join(list(args))
        self.logger.warn(f"notice operator info: {text}")
        text = f"{self.slug}:\n```\n" + text + "\n```"
        msg = pack_message(pack_post_data(text), self.operation.notice_info_conv_id)
        self.blaze.send_message(msg)

    @staticmethod
    def add_replying_text_message(
        ctx: MessageHandlerContext, text, quote_current_msg=False
    ):
        if quote_current_msg:
            msg = pack_message(
                pack_text_data(text),
                ctx.msgview.conversation_id,
                quote_message_id=ctx.msgview.message_id,
            )
        else:
            msg = pack_message(pack_text_data(text), ctx.msgview.conversation_id)
        ctx.replying_msgs.append(msg)

    @staticmethod
    def add_replying_markdown_message(ctx: MessageHandlerContext, text):
        msg = pack_message(pack_post_data(text), ctx.msgview.conversation_id)
        ctx.replying_msgs.append(msg)

    @staticmethod
    def add_replying_buttons_message(ctx: MessageHandlerContext, button_tuple_list):
        """
        button_tuple_list: [(label, action, color), ...]
        """
        count = 0
        buttons = []
        for tup in button_tuple_list:
            count += 1
            label, action, color = tup
            buttons.append(pack_button(label, action, color))
            if count == 6:
                button_group = pack_button_group_data(buttons)
                msg = pack_message(button_group, ctx.msgview.conversation_id)
                ctx.replying_msgs.append(msg)
                buttons = []
                count = 0
        if buttons:
            button_group = pack_button_group_data(buttons)
            msg = pack_message(button_group, ctx.msgview.conversation_id)
            ctx.replying_msgs.append(msg)

    @staticmethod
    def add_replying_livecard_message(
        ctx: MessageHandlerContext,
        url: str,
        width: int,
        height: int,
        thumb_url: str = "",
        shareable: bool = True,
    ):
        data = pack_livecard_data(url, thumb_url, width, height, shareable)
        msg = pack_message(data, ctx.msgview.conversation_id)
        ctx.replying_msgs.append(msg)
