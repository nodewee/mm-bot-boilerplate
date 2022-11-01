import json
from dataclasses import dataclass
from typing import List, Union

from mixinsdk.types.message import MessageView


@dataclass(frozen=True)
class _UserAddrTypes:
    MIXIN_GROUP: str = "MIXIN_GROUP"
    MIXIN_USER: str = "MIXIN_USER"
    MIXIN_APP: str = "MIXIN_APP"


MM_ADDR_TYPES = _UserAddrTypes()


class MixinMessageUser:
    def __init__(self):
        self.user_id = None
        self.user_type = None
        self.conversation_id = None

        self.is_in_group = None
        self.group_owner_user_id = None
        self.group_admin_user_id_list = []
        self.group_name = None

        self.mm_addr_type = None
        self.mm_addr_uid = None




class OperationObject:
    def __init__(self):
        self.operator_user_id: str = None
        self.operator_mixin_number: str = None
        self.notice_error_conv_id: str = None
        self.notice_info_conv_id: str = None

    @classmethod
    def from_payload(cls, payload: Union[dict, str]) -> "OperationObject":

        if isinstance(payload, str):
            payload = json.loads(payload)

        operator = payload.get("operator", {})
        notification = payload.get("notification", {})
        c = cls()
        c.operator_user_id = operator["user_id"]
        c.operator_mixin_number = operator["mixin_number"]
        c.notice_error_conv_id = notification["error"]["conversation_id"]
        c.notice_info_conv_id = notification["info"]["conversation_id"]

        return c

    @classmethod
    def from_file(cls, file_path: str) -> "OperationObject":
        with open(file_path, "rt") as f:
            return cls.from_payload(f.read())


class MessageHandlerContext:
    def __init__(self, msguser: MixinMessageUser, msgview: MessageView):
        self.msguser = msguser
        self.msgview = msgview
        self.replying_msgs: List[dict] = []
