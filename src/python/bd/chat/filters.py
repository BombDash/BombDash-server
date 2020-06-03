import bd
import ba._hooks


def filter_chat_message(client_id: int, msg: str):
    if bd.chat.process_command(client_id, msg):
        return
    return msg


old_filter = ba._hooks.filter_chat_message


def new_ba_filter_chat_message(msg: str, client_id: int):
    msg = old_filter(msg, client_id)
    return filter_chat_message(client_id, msg)


ba._hooks.filter_chat_message = new_ba_filter_chat_message
