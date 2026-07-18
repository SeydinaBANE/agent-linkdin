import anthropic


def build_client(api_key: str, base_url: str) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=api_key, base_url=base_url)


def message_text(message: anthropic.types.Message) -> str:
    return "".join(block.text for block in message.content if block.type == "text")
