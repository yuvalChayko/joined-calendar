def unpack(data):
    """
    unpack the data the server sent occording to the protocol
    :param data: str
    :return: opcode and list of params
    """
    opcode = data[:2]
    params = data[2:].split(",")

    return (opcode, params)

def pack_login(status):
    """
    pack msg according to the protocol
    :param status:
    :return:
    """
    return f"00{status}"

def pack_sign_up(status):
    """
    pack msg according to the protocol
    :param status:
    :return:
    """
    return f"01{status}"

def pack_new_calendar(status, data_or_not_existing_participants):
    """
    pack msg according to the protocol
    :param status:
    :param data_or_not_existing_participants:
    :return:
    """
    if status == "0":
        data_or_not_existing_participants[3] = "*".join(data_or_not_existing_participants[3])
    print(data_or_not_existing_participants)
    data_or_not_existing_participants = "^".join(data_or_not_existing_participants)

    return f"02{status},{data_or_not_existing_participants}"

def pack_new_event(status, id_or_not_existing_participants):
    """
    pack msg according to the protocol
    :param status:
    :param id_or_not_existing_participants:
    :return:
    """
    if status == "1":
        if id_or_not_existing_participants:
            id_or_not_existing_participants = "^".join(id_or_not_existing_participants)

    return f"04{status},{id_or_not_existing_participants}"

def pack_event_info(date, color):
    """
    pack msg according to the protocol
    :param date:
    :param color:
    :return:
    """
    return f"05{date},{color}"

def pack_there_is_an_invitation():
    """
    pack msg according to the protocol
    :return:
    """
    return f"10"

def pack_new_calendar_participant(status, calendar_id, username):
    """
    pack msg according to the protocol
    :param status:
    :param calendar_id:
    :param username:
    :return:
    """
    return f"11{status},{calendar_id},{username}"

def pack_event_invitation_succeed(status, username, name_event, name_calendar):
    """
    pack msg according to the protocol
    :param status:
    :param username:
    :param name_event:
    :param name_calendar:
    :return:
    """
    return f"13{status},{username},{name_event},{name_calendar}"

def pack_invitations(invitations):
    """
    pack msg according to the protocol
    :param invitations:
    :return:
    """
    if not invitations:
        invitations = []
    invitations = ["^".join(x) for x in list(invitations)]
    invitations = "*".join(invitations)
    return f"14{invitations}"

def pack_is_calendar_invitation_work(status):
    """
    pack msg according to the protocol
    :param status:
    :return:
    """
    return f"15{status}"

def pack_calendar_name_edit(status, calendar_id, name):
    """
    pack msg according to the protocol
    :param status:
    :param calendar_id:
    :param name:
    :return:
    """
    return f"20{status},{calendar_id},{name}"

def pack_event_name_edit(status, calendar_id, event_id , name):
    """
    pack msg according to the protocol
    :param status:
    :param calendar_id:
    :param event_id:
    :param name:
    :return:
    """
    return f"21{status},{calendar_id},{event_id},{name}"

def pack_time_edit(status, calendar_id, event_id, time_or_participants):
    """
    pack msg according to the protocol
    :param status:
    :param calendar_id:
    :param event_id:
    :param time_or_participants:
    :return:
    """

    time_or_participants = "^".join(time_or_participants)
    return f"22{status},{calendar_id},{event_id},{time_or_participants}"

def pack_event_dalete(status, event_id):
    """
    pack msg according to the protocol
    :param status:
    :param event_id:
    :return:
    """
    return f"30{status},{event_id}"

def pack_exit_calendar(calendar_id, username):
    """
    pack msg according to the protocol
    :param calendar_id:
    :param username:
    :return:
    """
    return f"31{calendar_id},{username}"

def pack_calendar_ids(calendar_ids):
    """
    pack msg according to the protocol
    :param calendar_ids:
    :return:
    """
    calendar_ids = "^".join(calendar_ids)
    return f"40{calendar_ids}"

def pack_day_events(day_events):
    """
    pack msg according to the protocol
    :param day_events:
    :return:
    """
    if not day_events:
        day_events = []
    day_events = ["^".join(x) for x in list(day_events)]
    day_events = "*".join(day_events)
    return f"41{day_events}"

def pack_month_events(month_events):
    """
    pack msg according to the protocol
    :param month_events:
    :return:
    """
    if not month_events:
        month_events = []
    month_events = ["^".join(x) for x in list(month_events)]
    month_events = "*".join(month_events)
    return f"42{month_events}"

def pack_key(key):
    """
    pack msg according to the protocol
    :param key:
    :return:
    """
    return f"50{key}"