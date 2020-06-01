import bd


def filter_chat_message(client_id: int, msg: str):
    if bd.chat.process_command(client_id, msg):
        return
    return msg
