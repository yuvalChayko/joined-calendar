from client_comm import ClientComm
import queue
import client_protocol as protocol
from datetime import datetime
import time


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

    status, data_or_not_existing_participants = params

    if status == "0":
        calendar_id, name, manager, participants = data_or_not_existing_participants.split("^")
        participants = participants.split("*")
        current_calendar.append([calendar_id, name, manager, participants])
        user_calendars.append(calendar_id)
        print(current_calendar)
        print(user_calendars)
        print(f"new calendar {data_or_not_existing_participants}")
    else:
        print("couldnt open calendar because", ", ".join(data_or_not_existing_participants.split("^")), "do not exist")


def new_calendar(name, participants):
    """
    send to server to add a new calendar
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
    send new eveent
    :return:
    """
    if "^" in name or "*" in name or "," in name:
        print("name not valid")
    else:
        comm.send(protocol.pack_new_event(calendar_id, name, start, end, date, participants))


def handle_event_info(params):
    """
    put on screen dot that represent the event. add event to month_event and if already exists, replace it.
    :param params: date, color
    :return:
    """
    date, color = params
    if date in month_event.keys():
        del month_event[date]
        print("remove events dot from screen")
    if color:
        month = date[3: 5]
        if month == current_month:
            month_event[date] = color
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


def invite_to_calendar(username, calendar_id):
    """
    send invitation to server
    :param username:
    :param calendar_id:
    :return:
    """
    comm.send(protocol.pack_calendar_invitation(calendar_id, username))


def handle_add_participant_to_calendar(params):
    """
    if the calendar is the current calendar on screen, add participant to participant list and show on screen
    :param params:
    :return:
    """
    status, calendar_id, username = params
    if current_calendar[0] == calendar_id:
        current_calendar[1].append(username)
        print(f"{username} joined the calendar")


def response_to_calendar_invitation(status, calendar_id):
    """
    send the response
    :param status:
    :param calendar_id:
    :return:
    """
    comm.send((protocol.pack_calendar_response(status, calendar_id)))


def handle_there_is_an_invitation(params):
    """
    show that there is invitations
    :param params:
    :return:
    """
    print("there is an invitation")


def handle_is_event_invitation_work(params):
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
        print("couldnt add invitation because username do not exists in calendar")
    elif status == "5":
        print("couldnt add invitation because invitation already exists")
    elif status == "6":
        print("couldnt add invitation because username already exists in event")


def response_event_invitation(status, event_id):
    """
    send the response
    :param status:
    :param event_id:
    :return:
    """
    comm.send((protocol.pack_event_response(status, event_id)))


def change_name_of_calendar(name, calendar_id):
    """
    change name of calendar
    :param name:
    :param calendar_id:
    :return:
    """
    if name == "personal" or "^" in name or "*" in name or "," in name:
        print("name not valid")
    else:
        comm.send(protocol.pack_calendar_name_edit(calendar_id, name))


def handle_calendar_name_change(params):
    """
    change name of calendar on screen
    :param params: status, calendar_id, name
    :return:
    """
    status, calendar_id, name = params
    if status == "0":
        if current_calendar[0] == calendar_id:
            current_calendar[2] = name
            print("there is a new name for the calendar")
    else:
        print("couldnt change name of calendar because you are not the manager")


def change_name_of_event(name, event_id):
    """
    change name of event
    :param name:
    :param event_id:
    :return:
    """
    if "^" in name or "*" in name or "," in name:
        print("name not valid")
    else:
        comm.send(protocol.pack_event_name_edit(event_id, name))


def handle_event_name_change(params):
    """
    tell the user if succeed or not
    :param params: status, calendar_id, event_id, name
    :return:
    """
    status, calendar_id, event_id, name = params
    if status == '0':
        day_events[2] = name
        print("name of event changed successfully")
    else:
        print("you are not the manager so couldnt change name of event")


def change_time(event_id, start, end, date):
    """
    change time of event
    :param event_id:
    :param start:
    :param end:
    :param date:
    :return:
    """
    date_format = "%d.%m.%Y"
    time_format = "%H:%M"
    try:
        time.strptime(start, time_format)
        time.strptime(end, time_format)
        flag = bool(datetime.strptime(date, date_format))
    except:
        flag = False

    if flag:
        flag = len(start) == 5 and len(end) == 5 and len(date) == 10 and (int(start[:2]) < int(end[:2]) or (int(start[:2]) == int(end[:2])and int(start[3:]) < int(end[3:])))

    if flag:
        comm.send(protocol.pack_event_time_edit(event_id, start, end, date))
    else:
        print("not valid time")

def handle_time_change(params):
    """
    shoe change of time or show why couldnt change
    :param params: status, calendar_id, event_id, time_or_participants
    :return:
    """
    status, calendar_id, event_id, time_or_participants = params
    if status == "1":
        participants = time_or_participants.split("^")
        print(f"couldnt change time because {', '.join(participants)} are not free at this time")
    elif status == "0":
        start, end, date = time_or_participants
        print("time change succeed")
    else:
        print("event do not exist so cant change its time")


if __name__ == '__main__':
    msg_q = queue.Queue()
    comm = ClientComm('127.0.0.1', 4500, msg_q)
    opcodes = {"00": handle_login, "01": handle_sign_up, "02": handle_new_calendar, "04": handle_new_event,
               "05": handle_event_info}
    current_calendar = [] # id, participants, name
    month_event = {}  # date: color
    current_month = ""
    day_events = ["1", "01.01.2024", "hello", "18:00", "20:00", "amit", ["amit", "alon", "yuval"]]  # [id, date, name, start, end, manager, [participants]]
    current_day = ""
    user_calendars = []
    invitations = []

    login("test1", "1234")
    sign_up("test4", "1234", "4444444444")
    new_calendar("hello", ["test2", "test3"])
    new_event("1", "hello", ["test2"], "20:00", "21:00", "11.03.2024")
    while True:
        msg = msg_q.get()
        opcode, params = protocol.unpack(msg)
        print(f'got from server: {msg}')
        if opcode in opcodes:
            print(opcodes[opcode](params))
        else:
            print(f'command number {opcode} not in dictionary')
