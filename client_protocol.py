def unpack(data):
    """
    unpack the data the server sent occording to the protocol
    :param data: str
    :return: opcode and list of params
    """
    opcode = data[:2]
    params = data[3:].split(",")

    # if opcode == "00" or opcode == "01":
    #     params = data[2:]
    # elif opcode == "02":
    #     if data[3:].is_numric():
    #         params = [data[2], data[3:]]
    #     else:
    #         params = [data[2], data[3:].split("^")]
    # elif opcode == "03" or opcode == "04":
    #     if len(data[2:]) > 1:
    #         params = [data[2], data[3:]]
    #     else:
    #         params = data[2]
    # elif opcode == "05" or opcode == "10":
    #     params = data[2:].split("$")
    # elif opcode == "10":
    #     pass


    return opcode, params


def pack_login(username, password):
    """
    pack msg according to the protocol
    :param username:
    :param password:
    :return:
    """
    return f"00,{username},{password}"

def pack_signup(username, password, phone_number):
    """
   pack msg according to the protocol
   :param username:
   :param password:
   :param phone_number
   :return:
   """
    return f"01,{username},{password},{phone_number}"

def pack_new_calendar(name, participants, manager):
    """
    msg according to the protocol
    :param name:
    :param participants:
    :param manager:
    :return:
    """
    participants = "^".join(participants)
    return f"02,{name},{participants},{manager}"

def pack_new_event(calendar_id, name, start, end, date, participants, manager):
    """
    msg according to the protocol
    :param calendar_id:
    :param name:
    :param start:
    :param end:
    :param date:
    :param participants:
    :param manager:
    :return:
    """
    participants = "^".join(participants)
    return f"04,{calendar_id},{name},{start},{end},{date},{participants},{manager}"

def pack_event_info(calendar_id, event_id):
    """
    msg according to the protocol
    :param calendar_id:
    :param event_id:
    :return:
    """
    return f"05,{calendar_id},{event_id}"

def pack_calendar_invitation(calendar_id, username, invited_by):
    """
    msg according to the protocol
    :param calendar_id:
    :param username:
    :param invited_by:
    :return:
    """
    return f"10,{calendar_id},{username},{invited_by}"

