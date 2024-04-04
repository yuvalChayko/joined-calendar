def unpack(data):
    """
    unpack the data the server sent occording to the protocol
    :param data: str
    :return: opcode and list of params
    """
    opcode = data[:2]
    params = data[2:].split(",")
    return opcode, params


def pack_login(username, password):
    """
    pack msg according to the protocol
    :param username:
    :param password:
    :return:
    """
    return f"00{username},{password}"

def pack_signup(username, password, phone_number):
    """
   pack msg according to the protocol
   :param username:
   :param password:
   :param phone_number
   :return:
   """
    return f"01{username},{password},{phone_number}"

def pack_new_calendar(name, participants):
    """
    pack msg according to the protocol
    :param name:
    :param participants:
    :return:
    """
    participants = "^".join(participants)
    return f"02{name},{participants}"

def pack_new_event(calendar_id, name, start, end, date, participants):
    """
    pack msg according to the protocol
    :param calendar_id:
    :param name:
    :param start:
    :param end:
    :param date:
    :param participants:
    :return:
    """
    participants = "^".join(participants)
    return f"04{calendar_id},{name},{start},{end},{date},{participants}"

def pack_calendar_invitation(calendar_id, username):
    """
    pack msg according to the protocol
    :param calendar_id:
    :param username:
    :return:
    """
    return f"10{calendar_id},{username}"

def pack_calendar_response(status, calendar_id):
    """
    pack msg according to the protocol
    :param status:
    :param calendar_id:
    :return:
    """
    return f"11{status},{calendar_id}"

def pack_event_invitation(calendar_id, event_id, username):
    """
    pack msg according to the protocol
    :param calendar_id:
    :param event_id:
    :param username:
    :return:
    """
    return f"12{calendar_id},{event_id},{username}"

def pack_event_response(status, event_id):
    """
    pack msg according to the protocol
    :param status:
    :param event_id:
    :return:
    """
    return f"13{status},{event_id}"

def pack_invitations_request():
    """
    pack msg according to the protocol
    :return:
    """
    return "14"

def pack_calendar_name_edit(calendar_id, name):
    """
    pack msg according to the protocol
    :param calendar_id:
    :param name:
    :return:
    """
    return f"20{calendar_id},{name}"

def pack_event_name_edit(event_id, name):
    """
    pack msg according to the protocol
    :param event_id:
    :param name:
    :return:
    """
    return f"21{event_id},{name}"

def pack_event_time_edit(event_id, start, end, date):
    """
    pack msg according to the protocol
    :param event_id:
    :param start:
    :param end:
    :param date:
    :return:
    """
    return f"22{event_id},{start},{end},{date}"

def pack_event_delete(event_id):
    """
    pack msg according to the protocol
    :param event_id:
    :return:
    """
    return f"30{event_id}"

def pack_exit_calendar(calendar_id):
    """
    pack msg according to the protocol
    :param calendar_id:
    :return:
    """
    return f"31{calendar_id}"

def pack_calendar_ids():
    """
    pack msg according to the protocol
    :return:
    """
    return "40"

def pack_day_event(calendar_id, date):
    """
    pack msg according to the protocol
    :param calendar_id:
    :param date:
    :return:
    """
    return f"41{calendar_id},{date}"

def pack_month_events(calendar_id, month, year):
    """
    pack msg according to the protocol
    :param calendar_id:
    :param month:
    :param year:
    :return:
    """
    return f"42{calendar_id},{month},{year}"

def pack_key(key):
    """
    pack msg according to the protocol
    :param key:
    :return:
    """
    return f"50{key}"
