from client_comm import ClientComm
import queue
import threading
import client_protocol as protocol
from datetime import datetime
import time
from pubsub import pub
import wx
from graphics import MyFrame

class Params:

    def __init__(self):
        self.user_calendars = []
        self.current_day = []  # full date
        self.day_events = []
        self.current_month = []  # month and year
        self.invitations = []
        self.current_invitation = 0
        self.current_calendar = []  # [id, participants, name, manager]
        self.current_event = 0


def handle_login(params):
    """
    show if and why couldnt log in
    :param params: status
    :return:
    """
    msg_to_send = "succeed"
    if params[0] == "1":
        msg_to_send = "incorrect password"
        call_error("incorrect password")
    elif params[0] == "2":
        msg_to_send = "incorrect username"
        call_error("incorrect username")
    elif params[0] == "3":
        msg_to_send = "username already open on other computer"
        call_error("username already open on other computer")
    elif params[0] == "0":
        wx.CallAfter(pub.sendMessage, "hide", panel="login")

    return msg_to_send



def login(username, password):
    """
    try to log in
    :param username:
    :param password:
    :return:
    """
    if "^" in username or "*" in username or "," in username or "$" in username or "^" in password or "*" in password or "," in password or "$" in password or len(password) < 5:
        print("not valid input")
        call_error("not valid input")
    else:
        comm.send(protocol.pack_login(username, password))


def handle_sign_up(params):
    """
    show if and why couldnt sign up
    :param params:
    :return:
    """
    print("here")
    msg_to_send = "succeed"
    if params[0] == "1":
        msg_to_send = "username already taken"
        call_error("username already taken")
    elif params[0] == "0":
        wx.CallAfter(pub.sendMessage, "hide", panel="register")

    return msg_to_send


def sign_up(username, password, phone_number):
    """
    try to sign up
    :param username:
    :param password:
    :param phone_number:
    :return:
    """
    if "^" in username or "*" in username or "," in username or "$" in username or "^" in password or "*" in password or "," in password or "$" in password or len(password) < 5 or not phone_number.isdigit() or len(phone_number) != 10:
        call_error("not valid input")
        print("not valid input")
    else:
        comm.send(protocol.pack_signup(username, password, phone_number))

def call_error(error):
    """
    call error
    :param error:
    :return:
    """
    wx.CallAfter(pub.sendMessage, "error", error=error)


def handle_new_calendar(params):
    """
    add id to user_calendars and show the calendar, or show why couldnt create calendar
    :param params:
    :return:
    """

    status, data_or_not_existing_participants = params

    if status == "0":
        wx.CallAfter(pub.sendMessage, "hide", panel="new cal")
        calendar_id, name, manager, participants = data_or_not_existing_participants.split("^")
        participants = participants.split("*")
        for i in range(len(participants)):
            participants[i] = participants[i].split("$")
        global_params.current_calendar = [calendar_id, participants, name, manager]
        global_params.user_calendars.append(calendar_id)
        print(f"new calendar {data_or_not_existing_participants}")
        wx.CallAfter(pub.sendMessage, "show calendar", name=name, manager=manager, participants=participants)
    elif status == "9":
        calendar_id, name, manager, participants = data_or_not_existing_participants.split("^")
        participants = participants.split("*")
        print(participants)
        for i in range(len(participants)):
            participants[i] = participants[i].split("$")
        global_params.current_calendar = [calendar_id, participants, name, manager]
        print(f"new calendar {data_or_not_existing_participants}")
        print(calendar_id, name, manager, participants)
        wx.CallAfter(pub.sendMessage, "show calendar", name=name, manager=manager, participants=participants)
    else:
        error = ", ".join(data_or_not_existing_participants.split("^")) + "do not exist"
        call_error(error)
        print("couldnt open calendar because", ", ".join(data_or_not_existing_participants.split("^")), "do not exist")


def new_calendar(name, participants):
    """
    send to server to add a new calendar
    :param name:
    :param participants:
    :return:
    """
    if name == "personal" or "^" in name or "*" in name or "," in name or "$" in name:
        call_error("name can't be 'personal' or contain '^', '*', '$', ','")
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
    print("heree", id_or_not_existing_participants)
    if status == "1":
        if id_or_not_existing_participants == "user":
            call_error("can't invite yourself")
        elif id_or_not_existing_participants != "" and id_or_not_existing_participants != "[]":
            id_or_not_existing_participants = id_or_not_existing_participants.split("^")
            call_error(", ".join(id_or_not_existing_participants) + " do not exist in calendar")
        else:
            call_error("time isn't available")
            print("time isnt available")
    else:
        print("succeed - return to calendar screen")
        wx.CallAfter(pub.sendMessage, "hide", panel="new event")



def new_event(calendar_id, name, participants, start, end, date):
    """
    send new event
    :return:
    """
    flag = True
    if "^" in name or "*" in name or "," in name or "$" in name:
        call_error("name can't contain '^', '*', '$', ','")
        print("name not valid")
    else:

        time_format = "%H:%M"
        try:
            time.strptime(start, time_format)
            time.strptime(end, time_format)
        except:
            flag = False

        if flag:
            flag = len(start) == 5 and len(end) == 5 and (int(start[:2]) < int(end[:2]) or (int(start[:2]) == int(end[:2]) and int(start[3:]) < int(end[3:])))

        if not flag:
            call_error("time not valid")
        else:
            comm.send(protocol.pack_new_event(calendar_id, name, start, end, date, participants))


def handle_event_info(params):
    """
    put on screen dot that represent the event. add event to month_events and if already exists, replace it.
    :param params: date, color
    :return:
    """
    date, color = params
    if date in month_events.keys():
        del month_events[date]
        print("remove events dot from screen")

    if color:
        month = date[3: 5]
        if month == global_params.current_month:
            month_events[date] = color
            print("add events dot to screen")
    if color:
        wx.CallAfter(pub.sendMessage, "mark", dates=[[int(date[:2]), color]])
    else:
        wx.CallAfter(pub.sendMessage, "unmark", dates=[int(date[:2])])



def handle_is_calendar_invitation_work(params):
    """
    show if invitation succeed and if not why
    :param params: status
    :return:
    """
    error = ""
    status = params[0]
    if status == "0":
        print("invitation succeed")
        wx.CallAfter(pub.sendMessage, "hide", panel="new cal parti")
    elif status == "1":
        error = "couldnt add invitation because calendar do not exists"
    elif status == "2":
        error = "couldnt add invitation because you are not the manager"
    elif status == "3":
        error = "couldnt add invitation because user do not exists"
    elif status == "4":
        error = "couldnt add invitation because username already exists in calendar"
    elif status == "5":
        error = "couldnt add invitation because invitation already exists"
    if status != "0":
        call_error(error)


def invite_to_calendar(username, calendar_id):
    """
    send invitation to server
    :param username:
    :param calendar_id:
    :return:
    """
    if global_params.current_calendar[2] == "personal":
        call_error("can't invite to personal calendar")
    else:
        comm.send(protocol.pack_calendar_invitation(calendar_id, username))


def handle_add_participant_to_calendar(params):
    """
    if the calendar is the current calendar on screen, add participant to participant list and show on screen
    :param params:
    :return:
    """
    status, calendar_id, username = params
    if global_params.current_calendar[0] == calendar_id:
        global_params.current_calendar[1].append(username)
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
    wx.CallAfter(pub.sendMessage, "new invitation")
    print("there is an invitation")


def invite_to_event(username, calendar_id, event_id):
    """
    send invitation to server
    :param username:
    :param calendar_id:
    :param event_id:
    :return:
    """
    comm.send(protocol.pack_event_invitation(calendar_id, event_id, username))


def handle_is_event_invitation_work(params):
    """
    show if invitation succeed and if not why
    :param params: status
    :return:
    """
    error = ""
    status = params[0]
    if status == "0":
        print("invitation succeed")
        wx.CallAfter(pub.sendMessage, "hide", panel="new evt parti")
    elif status == "1":
        error = "couldnt add invitation because calendar do not exists"
    elif status == "2":
        error = "couldnt add invitation because you are not the manager"
    elif status == "3":
        error = "couldnt add invitation because user do not exists"
    elif status == "4":
        error = "couldnt add invitation because username do not exists in calendar"
    elif status == "5":
        error = "couldnt add invitation because invitation already exists"
    elif status == "6":
        error = "couldnt add invitation because username already exists in event"
    if status != '0':
        call_error(error)


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
    print(name, calendar_id)
    if name == "personal" or "^" in name or "*" in name or "," in name or "$" in name:
        print("name not valid")
        call_error("name can't be 'personal' or contain '^', '*', '$', ','")
    elif global_params.current_calendar[2] == "personal":
        call_error("can't change name of personal calendar")
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
        if global_params.current_calendar[0] == calendar_id:
            wx.CallAfter(pub.sendMessage, "hide", panel="cal name")
            global_params.current_calendar[2] = name
            wx.CallAfter(pub.sendMessage, "show calendar", name=name, manager=global_params.current_calendar[3], participants=global_params.current_calendar[1])
            dates = []
            for i in month_events.keys():
                dates += [[int(i[:2]), month_events[i]]]
            print(dates)
            wx.CallAfter(pub.sendMessage, "mark", dates=dates)
            print("there is a new name for the calendar")
    else:
        call_error("couldnt change name of calendar because you are not the manager")


def change_name_of_event(name, event_id):
    """
    change name of event
    :param name:
    :param event_id:
    :return:
    """
    if "^" in name or "*" in name or "," in name or "$" in name:
        call_error("name can't contain '^', '*', '$', ','")
        print("name not valid")
    else:
        comm.send(protocol.pack_event_name_edit(event_id, name))


def handle_event_name_change(params):
    """
    tell the user if succeed or not
    :param params: status, calendar_id, event_id, name
    :return:
    """
    status, event_id, name = params
    print(event_id, "event")
    print(global_params.day_events)
    if status == '0':
        print("day", global_params.day_events)
        current_event = [i for i in range(len(global_params.day_events)) if global_params.day_events[i][-1] == str(event_id)][-1]
        print(current_event)
        global_params.day_events[current_event][1] = name
        wx.CallAfter(pub.sendMessage, "hide", panel="evt name")
        wx.CallAfter(pub.sendMessage, "show day", event=global_params.day_events[global_params.current_event])
        print("name of event changed successfully")
    else:
        call_error("you are not the manager so couldnt change name of event")


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
        call_error("not valid input")
        print("not valid time")


def handle_time_change(params):
    """
    show change of time or show why couldnt change
    :param params: status, calendar_id, event_id, time_or_participants
    :return:
    """
    status, calendar_id, event_id, time_or_participants = params
    if status == "1":
        participants = time_or_participants.split("^")
        call_error(f"couldnt change time because {', '.join(participants)} are not free at this time")
    elif status == "0":
        start, end, date = time_or_participants.split("^")
        for i in range(len(global_params.day_events)):
            if global_params.day_events[i][-1] == event_id:
                global_params.day_events[i][4] = date
                global_params.day_events[i][2] = start
                global_params.day_events[i][3] = end
                wx.CallAfter(pub.sendMessage, "hide", panel="evt time")
                wx.CallAfter(pub.sendMessage, "show day", event=global_params.day_events[global_params.current_event])
        print("time change succeed")
    elif status == "2":
        call_error("couldnt change time because you are not the manager")
    else:
        call_error("event do not exist so cant change its time")


def delete_event(event_id):
    """
    try to delete the event
    :param event_id:
    :return:
    """
    comm.send(protocol.pack_event_delete(event_id))


def handle_delete_event(params):
    """
    show if succeed and if not why
    :param params: status, event_id
    :return:
    """
    error = ""
    status, event_id = params
    if status == "0":
        print("succeed")
        global_params.day_events.remove(global_params.day_events[global_params.current_event])
        wx.CallAfter(pub.sendMessage, "hide", panel="event")
        if len(global_params.day_events) == 0:
            wx.CallAfter(pub.sendMessage, "show day", event=global_params.current_day)
        elif global_params.current_event == len(global_params.day_events):
            global_params.current_event = global_params.current_event - 1
            wx.CallAfter(pub.sendMessage, "show day", event=global_params.day_events[global_params.current_event])
        else:
            global_params.current_event = global_params.current_event
            wx.CallAfter(pub.sendMessage, "show day", event=global_params.day_events[global_params.current_event])
    elif status == "1":
        error = "cant delete event because you are not the manager"
    else:
        error = "cant delete event because event do not exist"

    if status != "0":
        call_error(error)


def exit_calendar(calendar_id):
    """
    try to exit a calendar
    :param calendar_id:
    :return:
    """
    if global_params.current_calendar[2] == "personal":
        call_error("cant delete calendar because its a personal one")
    else:
        comm.send(protocol.pack_exit_calendar(calendar_id))


def handle_exit_calendar(params):
    """
    delete calendar participant
    :param params: username, calendar_id
    :return:
    """
    username, calendar_id = params
    if calendar_id == global_params.current_calendar[0]:
        print("participant exit from calendar")
        global_params.current_calendar[1].remove(username)


def handle_delete_calendar(params):
    """
    delete caledar from screen and from list of ids
    :param params: status, calendar_id
    :return:
    """
    status, calendar_id = params
    if status == "0":
        if global_params.current_calendar[0] == calendar_id:
            print("delete current calendar")
            print(global_params.user_calendars)
            if global_params.user_calendars.index(calendar_id) == (len(global_params.user_calendars)-1):
                get_calendar_info(global_params.user_calendars[-2])


            else:
                get_calendar_info(global_params.user_calendars[global_params.user_calendars.index(calendar_id)+1])
            wx.CallAfter(pub.sendMessage, "hide", panel="calendar")

        global_params.user_calendars.remove(calendar_id)
    else:
        call_error("couldnt delete calendar, please try again")


def get_calendar_ids():
    """
    try to get calendar ids
    :return:
    """
    comm.send(protocol.pack_calendar_ids())


def handle_calendar_ids(params):
    """
    save calendar ids in user_calendars
    :param params:
    :return:
    """
    calendar_ids = params[0]
    calendar_ids = calendar_ids.split("^")
    global_params.user_calendars = calendar_ids



def get_day_events(calendar_id, date):
    """
    try to get day events of calendar
    :param calendar_id:
    :param date:
    :return:
    """
    date_format = "%d.%m.%Y"
    try:
        flag = bool(datetime.strptime(date, date_format))
    except:
        flag = False

    if flag:
        comm.send(protocol.pack_day_event(calendar_id, date))
        global_params.current_day = date
    else:
        print("something went wrong - not valid date")


def handle_day_events(params):
    """
    show on screen the events, save day events in day_events
    :param params: day_events
    :return:
    """
    print(params)

    if params[0] != "":
        events = params[0].split("*")
        for i in range(len(events)):
            events[i] = events[i].split("^")
            events[i][0] = events[i][0].split("$")
        print(events)
        global_params.day_events = events
        global_params.current_event = 0
        print("got day events, show them on screen")
        event = events[0]
    else:
        global_params.day_events = []
        event = [global_params.current_day][0]

    wx.CallAfter(pub.sendMessage, "show day", event=event)


def get_month_events(calendar_id, month, year):
    """
    try to get month events of calendar
    :param calendar_id:
    :param month:
    :param year:
    :return:
    """
    if month.isnumeric() and year.isnumeric() and len(month) == 2 and len(year) == 4:
        comm.send(protocol.pack_month_events(calendar_id, month, year))
        global_params.current_month = month + "." + year
    else:
        print("something went wrong - not valid month and year")


def handle_month_events(params):
    """
    show month events on screen and save it on the dictionary
    :param params:
    :return:
    """
    events = params[0].split("*")
    month_events.clear()
    if len(events) > 0 and events[0] != "":
        for i in events:
            date, color = i.split("^")
            month_events[date] = color
    print("got month events - show them on screen")
    print(month_events)
    dates = []
    for i in month_events.keys():
        dates += [[int(i[:2]), month_events[i]]]
    print(dates)
    wx.CallAfter(pub.sendMessage, "mark", dates=dates)


def get_calendar_info(calendar_id):
    """
    try to get calendar info
    :param calendar_id:
    :return:
    """
    comm.send(protocol.pack_get_calendar_info(calendar_id))



# def handle_calendar_info(params):
#     """
#     show name, participants and month events on screen and save it on the dictionary
#     :param params:
#     :return:
#     """
#     name, participants, events = params[0].split("$")
#     participants = participants.split("*")
#     events = events.split("*")
#     if len(events) > 0 and events[0] != "":
#         for i in events:
#             date, color = i.split("^")
#             month_events[date] = color
#     print("got month events - show them on screennnnn")


def get_invitations():
    """
    try to get invitations
    :return:
    """
    comm.send(protocol.pack_invitations_request())


def handle_invitations(params):
    """
    get invitations and shoe them on screen
    :param params: invitations
    :return:
    """
    if params == [""]:
        wx.CallAfter(pub.sendMessage, "show invitation", params=[])
    else:
        print("hiiiiiiiiiiiii")
        print(params)
        invitations = params[0].split("*")
        print(invitations)
        for i in range(len(invitations)):
            invitations[i] = invitations[i].split("^")
            invitations[i][2] = invitations[i][2].split("$")
        global_params.invitations = invitations
        wx.CallAfter(pub.sendMessage, "show invitation", params=invitations[0])
        global_params.current_invitation = 0
    print(f"got invitations, show them on screen")


def handle_recv(msg_q):
    """
    handle msgs from server
    :param msg_q:
    :return:
    """
    while True:
        msg = msg_q.get()
        opcode, params = protocol.unpack(msg)
        print(f'got from server: {msg}')
        if opcode in opcodes:
            print(opcodes[opcode](params))
        else:
            print(f'command number {opcode} not in dictionary')


def handle_graphics(graphics_q):
    """
    handle msgs from graphics
    :param graphics_q:
    :return:
    """
    while True:
        msg = graphics_q.get()
        opcode, params = msg
        print(f'got from graphics: {msg}')
        if opcode == "register":
            username, password, phone = params
            sign_up(username, password, phone)
        elif opcode == "login":
            username, password = params
            login(username, password)
        elif opcode == "right":
            current = global_params.user_calendars.index(global_params.current_calendar[0])
            print("right calendar", current, len(global_params.user_calendars), global_params.user_calendars)
            if len(global_params.user_calendars) == (current+1):
                call_error("can't go more right")
            else:
                wx.CallAfter(pub.sendMessage, "hide", panel="calendar")
                get_calendar_info(global_params.user_calendars[current+1])

        elif opcode == "left":
            current = global_params.user_calendars.index(global_params.current_calendar[0])
            print("left calendar", current, len(global_params.user_calendars), global_params.user_calendars)
            if current == 0:
                call_error("can't go more left")
            else:
                get_calendar_info(global_params.user_calendars[current-1])
                wx.CallAfter(pub.sendMessage, "hide", panel="calendar")
        elif opcode == "month":
            month, year = params
            global_params.current_month = [month, year]
            dates = []
            for i in month_events.keys():
                dates += [int(i[:2])]
            wx.CallAfter(pub.sendMessage, "unmark", dates=dates)
            month_events.clear()
            get_month_events(global_params.current_calendar[0], month, year)
        elif opcode == "day":
            date = params
            # wx.CallAfter(pub.sendMessage, "hide", panel="calendar")
            get_day_events(global_params.current_calendar[0], date)
        elif opcode == "left event":
            if global_params.current_event == 0:
                call_error("can't go more left")
            else:
                global_params.current_event = global_params.current_event - 1
                wx.CallAfter(pub.sendMessage, "hide", panel="event")
                wx.CallAfter(pub.sendMessage, "show day", event=global_params.day_events[global_params.current_event])
        elif opcode == "right event":
            if (global_params.current_event + 1) == len(global_params.day_events):
                call_error("can't go more right")
            else:
                global_params.current_event = global_params.current_event + 1
                wx.CallAfter(pub.sendMessage, "hide", panel="event")
                wx.CallAfter(pub.sendMessage, "show day", event=global_params.day_events[global_params.current_event])
        elif opcode == "invitations":
            wx.CallAfter(pub.sendMessage, "hide", panel="calendar")
            get_invitations()
        elif opcode == "left invitation":
            if global_params.current_invitation == 0:
                call_error("can't go more left")
            else:
                global_params.current_invitation = global_params.current_invitation - 1
                wx.CallAfter(pub.sendMessage, "hide", panel="invitation")
                wx.CallAfter(pub.sendMessage, "show invitation", params=global_params.invitations[global_params.current_invitation])
        elif opcode == "right invitation":
            if (global_params.current_invitation + 1) == len(global_params.invitations):
                call_error("can't go more right")
            else:
                global_params.current_invitation = global_params.current_invitation + 1
                wx.CallAfter(pub.sendMessage, "hide", panel="invitation")
                wx.CallAfter(pub.sendMessage, "show invitation", params=global_params.invitations[global_params.current_invitation])
        elif opcode == "response":
            wx.CallAfter(pub.sendMessage, "hide", panel="invitation")
            if len(global_params.invitations[global_params.current_invitation]) > 5:
                response_event_invitation(params[0], global_params.invitations[global_params.current_invitation][-1])
            else:
                response_to_calendar_invitation(params[0], global_params.invitations[global_params.current_invitation][-1])
            global_params.invitations.remove(global_params.invitations[global_params.current_invitation])

            if len(global_params.invitations) != 0:
                if not (params[0] == "0" and len(global_params.invitations[global_params.current_invitation]) < 5):
                    if len(global_params.invitations) == global_params.current_invitation - 1:
                        global_params.current_invitation = 0
                    wx.CallAfter(pub.sendMessage, "show invitation", params=global_params.invitations[global_params.current_invitation])
            else:
                wx.CallAfter(pub.sendMessage, "show invitation", params=[])
        elif opcode == "new cal parti":
            for i in params:
                invite_to_calendar(i, global_params.current_calendar[0])
        elif opcode == "new cal":
            name, users = params
            new_calendar(name, users)
        elif opcode == "new evt parti":
            for i in params:
                invite_to_event(i, global_params.current_calendar[0], global_params.day_events[global_params.current_event][-1])
        elif opcode == "new event":
            new_event(global_params.current_calendar[0], params[0], params[1], params[2], params[3], params[4])
        elif opcode == "del evt":
            delete_event(global_params.day_events[global_params.current_event][-1])
        elif opcode == "exit cal":
            exit_calendar(global_params.current_calendar[0])
        elif opcode == "cal name":
            change_name_of_calendar(params, global_params.current_calendar[0])
        elif opcode == "evt name":
            print("nameeeeeeee", global_params.day_events[global_params.current_event], params)
            change_name_of_event(params, global_params.day_events[global_params.current_event][-1])
        elif opcode == "evt time":
            change_time(global_params.day_events[global_params.current_event][-1], params[1], params[2], params[0])
        else:
            print(f'command {opcode} not valid')



if __name__ == '__main__':
    msg_q = queue.Queue()
    graphics_q = queue.Queue()
    comm = ClientComm('127.0.0.1', 4500, msg_q)
    opcodes = {"00": handle_login, "01": handle_sign_up, "02": handle_new_calendar, "04": handle_new_event,
               "05": handle_event_info, "10": handle_there_is_an_invitation, "11": handle_add_participant_to_calendar,
               "13": handle_is_event_invitation_work, "14": handle_invitations, "15": handle_is_calendar_invitation_work,
               "20": handle_calendar_name_change, "21": handle_event_name_change, "22": handle_time_change,
               "30": handle_delete_event, "31": handle_delete_calendar, "32": handle_exit_calendar, "40": handle_calendar_ids,
               "41": handle_day_events, "42": handle_month_events}
    month_events = {}  # date: color
    global_params = Params()
    global_params.day_events = [["1", "01.01.2024", "hello", "18:00", "20:00", "amit", ["amit", "alon", "yuval"]]]  # [id, date, name, start, end, manager, [participants]]
    # global_params.current_calendar = ["58", ["test1", "test2"], "test", "test1"]  # id, participants, name, manager


    # login("test2", "1234")
    # sign_up("test4", "1234", "4444444444")
    # new_calendar("hello", ["test3"])
    # new_event("1", "hello", ["test2"], "20:00", "21:00", "18.03.2024")
    # invite_to_calendar("test1", '21')
    # invite_to_calendar("test1", '1')
    # response_to_calendar_invitation("0", '21')
    # response_to_calendar_invitation("1", '21')
    # invite_to_event("test3", "1", "1")
    # response_event_invitation("0", "9")
    # change_name_of_calendar("new name", "1")
    # change_name_of_event("new name", "1")
    # change_time("10", "18:00", "20:00", "21.03.2024")
    # change_time("9", "18:00", "21:00", "17.03.2024")
    # change_time("9", "18:00", "21:00", "20.03.2024")
    # delete_event("10")
    # delete_event("9")
    # exit_calendar("58")
    # get_calendar_ids()
    # get_day_events("1", "12.02.2024")
    # get_month_events("1", "03", "2024")
    # get_invitations()


    threading.Thread(target=handle_recv, args=(msg_q,)).start()
    threading.Thread(target=handle_graphics, args=(graphics_q,)).start()


    app = wx.App(False)
    frame = MyFrame(graphics_q)
    frame.Show()
    app.MainLoop()

    # while True:
    #     msg = msg_q.get()
    #     opcode, params = protocol.unpack(msg)
    #     print(f'got from server: {msg}')
    #     if opcode in opcodes:
    #         print(opcodes[opcode](params))
    #     else:
    #         print(f'command number {opcode} not in dictionary')
