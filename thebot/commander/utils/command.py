import json

command_mapping = None


def load_command_mapping(reload: bool = False):
    global command_mapping
    if command_mapping is not None and not reload:
        return command_mapping

    from pathlib import Path

    data_path = Path(__file__).absolute().parent.parent.joinpath("commands.json")
    command_mapping = json.load(open(data_path))
    print(f"Loaded {data_path}")

    return command_mapping


def parse_cmd_from_mixin_msg_text(text: str):
    """
    return mm_cmd,mm_args
    """
    text = text.strip()
    if not text:
        raise ValueError("command is empty")

    first_blank_pos = text.find(" ")
    if first_blank_pos > -1:
        mm_cmd = text[:first_blank_pos].lower()
        mm_args = text[first_blank_pos + 1 :]
    else:
        mm_cmd = text.lower()
        mm_args = ""
    return mm_cmd, mm_args


def parse_options_and_arguments(text: str):
    """return options, arguments"""
    in_quotation = False

    options = []
    arguments = []

    field = ""
    fields = []
    for char in text:
        if char == '"':
            in_quotation = not in_quotation
            continue
        elif char == " ":
            if in_quotation:
                field += " "
                continue
            else:
                fields.append(field)
                field = ""
        else:
            field += char
    if field:
        fields.append(field)

    for field in fields:
        if field.startswith("-"):
            options.append(field.lstrip("-"))
        else:
            arguments.append(field)

    return options, arguments
