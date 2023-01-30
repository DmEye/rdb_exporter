def decode_call_object_type(code):
    if code == 2:
        return "trigger"
    elif code == 5:
        return "procedure"
    elif code == 15:
        return "function"
    else:
        return "Unknown"


def decode_group(code):
    if code == 0:
        return "database"
    elif code == 1:
        return "connection"
    elif code == 2:
        return "transaction"
    elif code == 3:
        return "statement"
    elif code == 4:
        return "call"
    elif code == 5:
        return "cached_query"
    else:
        return "Unknown"


def check_none(to_check, default=-1) -> int:
    return default if to_check is None else to_check
