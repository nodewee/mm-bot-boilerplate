def render_cmd_doc_markdown(doc: dict):
    if not doc:
        return ""

    title = doc.get("title")
    syntax = doc.get("syntax")
    arguments = doc.get("arguments")
    options = doc.get("options")
    examples = doc.get("examples")

    md = ""
    if title:
        md += title + "\n"
    if syntax:
        md += f"\nSyntax: `{syntax}` \n"
    if options:
        md += "\nOptions\n"
        for key in options:
            md += f"- **{key}**\t{options[key]}"
    if arguments:
        md += "\nArguments\n"
        for key in arguments:
            md += f"- **{key}**\t{arguments[key]}"
    if examples:
        md += "\nExamples\n"
        for item in examples:
            cmd = item.get("cmd")
            desc = item.get("desc")
            md += f"- `{cmd}`, {desc}"

    return md


def dict_to_markdown_table(d: dict):
    t = "\n\n|key|value|"
    t += "\n|--|--|"
    for key in d:
        t += f"\n|{key}|{d[key]}|"
    t += "\n\n"
    return t


def dict_to_text_list(d: dict):
    t = "\n"
    for key in d:
        t += f"\n- {key}: {d[key]}"
    t += "\n"
    return t
