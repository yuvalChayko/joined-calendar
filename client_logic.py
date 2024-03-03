from client_comm import ClientComm
import queue
import client_protocol as protocol


def handle_login(params):
    """
    show if and why couldnt log in
    :param params: status
    :return:
    """
    msg_to_send = "succeed"
    if params[0] == "1":
        msg_to_send = "incorrect password"
    elif params[0] == "2":
        msg_to_send = "incorrect username"
    elif params[0] == 3:
        msg_to_send = "username already open on other computer"
    return msg_to_send


def login(username, password):
    """
    try to log in
    :param username:
    :param password:
    :return:
    """
    comm.send(protocol.pack_login(username, password))


def handle_sign_up(params):
    """
    show if and why couldnt sign up
    :param params:
    :return:
    """
    msg_to_send = "succeed"
    if params[0] == "1":
        msg_to_send = "username already taken"

    return msg_to_send


def sign_up(username, password, phone_number):
    """
    try to sign up
    :param username:
    :param password:
    :param phone_number:
    :return:
    """
    comm.send(protocol.pack_signup(username, password, phone_number))


def handle_new_calendar(params):
    """
    add id to user_calendars and show the calendar, or show why couldnt create calendar
    :param params:
    :return:
    """
    status, id_or_not_existing_participants = params
    if status == "0":
        user_calendars.append(id_or_not_existing_participants)
        print(f"open {id_or_not_existing_participants}")
    else:
        print("couldnt open calendar because", ", ".join(id_or_not_existing_participants.split("^")), "do not exist")


def new_calendar(name, participants):
    """

    :param name:
    :param participants:
    :return:
    """
    if name == "personal" or "^" in name or "*" in name or "," in name:
        print("name not valid")
    else:
        comm.send(protocol.pack_new_calendar(name, participants))


def handle_new_event(params):
    """
    if succeed add to screen, and if not show why.
    :param params: status, id_or_not_existing participants
    :return:
    """
    status, id_or_not_existing_participants = params
    if status == "1":
        if id_or_not_existing_participants != "":
            id_or_not_existing_participants = id_or_not_existing_participants.split("^")
            print("couldnt open event because", ", ".join(id_or_not_existing_participants), "do not exist in calendar")
        else:
            print("time isnt available")
    else:
        print("succeed - return to calendar screen")


def new_event(calendar_id, name, participants, start, end, date):
    """

    :return:
    """
    if "^" in name or "*" in name or "," in name:
        print("name not valid")
    else:
        comm.send(protocol.pack_new_event(calendar_id, name, start, end, date, participants))


def handle_event_info(params):
    """
    put on screen dot that represent the event. add event to month_event and if already exists, replace it.
    :param date:
    :param color:
    :param event_id:
    :return:
    """
    event_id, date, color = params
    if event_id in month_event.keys():
        del month_event[event_id]
        print("remove events dot from screen")
    month = date[3: 5]
    if month == current_month:
        month_event[event_id] = [color, date]
        print("add events dot to screen")


def handle_is_calendar_invitation_work(params):
    """
    show if invitation succeed and if not why
    :param params: status
    :return:
    """
    status = params[0]
    if status == "0":
        print("invitation succeed")
    elif status == "1":
        print("couldnt add invitation because calendar do not exists")
    elif status == "2":
        print("couldnt add invitation because you are not the manager")
    elif status == "3":
        print("couldnt add invitation because user do not exists")
    elif status == "4":
        print("couldnt add invitation because username already exists in calendar")
    elif status == "5":
        print("couldnt add invitation because invitation already exists")


def handle_calendar_invitation(params):
    """
    add invitations to invitation list and notify the user
    :param params: name, calendar_id, invited_by
    :return:
    """
    name, calendar_id, invited_by = params
    print("got new invitation")
    invitations.append([name, calendar_id, invited_by])


if __name__ == '__main__':
    msg_q = queue.Queue()
    comm = ClientComm('127.0.0.1', 4500, msg_q)
    opcodes = {"00": handle_login, "01": handle_sign_up, "02": handle_new_calendar, "04": handle_new_event,
               "05": handle_event_info}
    current_calendar = ""
    month_event = {}  # id: [color, date]
    current_month = ""
    current_day = ""
    user_calendars = []
    invitations = []

    login("test1", "1234")
    sign_up("test4", "1234", "4444444444")
    new_calendar("hello", ["test2", "test3"])
    new_event("1", "hello", ["test2"], "20:00", "21:00", "09.03.2024")
    while True:
        msg = msg_q.get()
        opcode, params = protocol.unpack(msg)
        print(f'got from server: {msg}')
        if opcode in opcodes:
            print(opcodes[opcode](params))
        else:
            print(f'command number {opcode} not in dictionary')
