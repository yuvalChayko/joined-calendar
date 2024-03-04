from server_comm import ServerComm
import queue
import server_protocol as protocol
from joined_calendar_db import joined_calendar_db as data_base
import hashlib
from datetime import datetime

def handle_login(ip, params):
    """
    check if password and username correct and return msg accordingly. if succeed - send to the client his calendar ids and his invitations.
    :param ip:
    :param params: username, password
    :return:
    """
    username, password = params
    status = 0
    msgs_to_send = []
    if not db.is_user_exists(username):
        status = 2
    elif db.get_password(username) != hashlib.sha256(password.encode()).digest():
        status = 1
    elif username in current_users.keys():
        status = 3
    else:
        msgs_to_send += [db.get_user_calendars(username)]
        msgs_to_send += [db.get_calendar_invitations(username).append(db.get_event_invitations(username))]
    comm.send(ip, protocol.pack_login(status))
    if len(msgs_to_send) != 0:
        comm.send(ip, protocol.pack_calendar_ids(msgs_to_send[0]))
        comm.send(ip, protocol.pack_invitations(msgs_to_send[1]))
        current_users[username] = ip


def handle_sign_up(ip, params):
    """
    try to open a username and return msg if available or if taken. if available, add user and add him a private calendar and send it to him
    :param ip:
    :param params: username, password, phone
    :return:
    """
    username, password, phone_number = params
    status = 1
    msg = ""
    if not db.is_user_exists(username):
        status = 0

        db.add_user(username, password, phone_number)
        db.add_calendar("personal", username)
        msg = protocol.pack_calendar_ids(db.get_user_calendars(username))
        current_users[username] = ip
    comm.send(ip, protocol.pack_sign_up(status))
    if msg:
        comm.send(ip, msg)

def handle_new_calendar(ip, params):
    """
    check if every participant is an existing user and if so, create the calendar and add invitations. send status if succeed. if succeed send id and if not send why
    :param ip:
    :param params: name, participants
    :return:
    """
    print(current_users)
    print(i for i in current_users)
    username = [i for i in current_users if current_users[i] == ip][0]
    name, participants = params
    participants = participants.split("^")
    not_existing_participants = [i for i in participants if not db.is_user_exists(i)]
    if not not_existing_participants:
        id = db.add_calendar(name, username)
        comm.send(ip, protocol.pack_new_calendar("0", [id, name, username, [username]]))
        for i in participants:
            db.add_calendar_invitation(id, username, i)
            if i in current_users:
                comm.send(current_users[i], protocol.pack_calendar_invitation(name, id, username))
    else:
        comm.send(ip, protocol.pack_new_calendar("1", not_existing_participants))


def handle_new_event(ip, params):
    """
    check if time is available and if so add event. add invitations if participants in the calendar. send to participants that the calendar is open on their screen the info(color, date)
    :param ip:
    :param params: calendar_id, name, start, end, date, participants
    :return:
    """
    calendar_id, name, start, end, date, participants = params
    participants = participants.split("^")
    username = [i for i in current_users if current_users[i] == ip][0]
    not_existing_participants = [i for i in participants if not db.is_user_exists(i)]
    if not not_existing_participants:
        not_in_calendar = [i for i in participants if not db.is_participant_exists_in_calendar(calendar_id, i)]
    not_existing_participants = list(set(not_existing_participants).union(set(not_in_calendar)))
    if not_existing_participants:
        comm.send(ip, protocol.pack_new_event("1", not_existing_participants))
    else:
        if db.check_is_time_available(username, start, end, date):
            event_id = db.add_event(name, participants, calendar_id, username, start, end, date)
            comm.send(ip, protocol.pack_new_event("0", event_id))
            for p in participants:
                db.add_event_invitation(event_id, calendar_id, p, username)
                if p in current_users:
                    comm.send(current_users[p], protocol.pack_event_invitation(calendar_id, event_id, name, username, start, end, date))
            date, color = get_event_info(event_id, calendar_id)
            comm.send(ip, protocol.pack_event_info(event_id, date, color))
            for user in current_open_calendars:
                month = date[3:]
                if month == current_open_calendars[user][1] and db.is_participant_exists_in_calendar(current_open_calendars[user][0]):
                    date, color = get_event_info(event_id, current_open_calendars[user][0])
                    comm.send(current_users[user], protocol.pack_event_info(event_id, date, color))

        else:
            comm.send(ip, protocol.pack_new_event("1", ""))


def get_event_info(event_id, calendar_id):
    """
    return the color of the event, the id and the date.
    :param event_id:
    :param calendar_id:
    :return:
    """
    return db.get_some_event_info(event_id, calendar_id)


def handle_calendar_invitation(ip, params):
    """
    if calendar exists, invited_by is manager, username exists and not already in calendar or invitation already exists, add invitation to table and if username is in current_users send him the invitation
    :param params: calendar_id, username, invited_by
    :return:
    """
    calendar_id, username = params
    invited_by = [i for i in current_users if current_users[i] == ip][0]
    if db._is_calendar_exists(calendar_id):
        comm.send(ip, protocol.pack_is_calendar_invitation_work("1"))
    elif db.is_manager_calander(calendar_id, invited_by):
        comm.send(ip, protocol.pack_is_calendar_invitation_work("2"))
    elif db.is_user_exists(username):
        comm.send(ip, protocol.pack_is_calendar_invitation_work("3"))
    elif not db.is_participant_exists_in_calendar(username):
        comm.send(ip, protocol.pack_is_calendar_invitation_work("4"))
    elif not db.is_calendar_invitation_exists(calendar_id, username):
        comm.send(ip, protocol.pack_is_calendar_invitation_work("5"))
    else:
        comm.send(ip, protocol.pack_is_calendar_invitation_work("0"))
        db.add_calendar_invitation(calendar_id, invited_by, username)
        if username in current_users.keys():
            comm.send(current_users[username], protocol.pack_calendar_invitation(db.get_calendar_info(calendar_id)[0], calendar_id, invited_by))


def handle_is_calendar_accepted(ip, params):
    """
    if accepted - add participant to table, send calendar in current month to user, send users that are currently looking on the calendar the new participant, remove invitation
    if declined - remove invitation from table
    :param ip:
    :param params: status, calendar_id
    :return:
    """
    status, calendar_id = params
    username = [i for i in current_users if current_users[i] == ip][0]
    db.delete_calendar_invitation(username, calendar_id)
    if status == "0":
        db.add_calendar_participant(calendar_id, username)
        today = datetime.now()
        info = db.get_calendar_info(calendar_id)
        print(info, "info")
        comm.send(ip, protocol.pack_new_calendar(status, [calendar_id, info[0], info[1], info[2]]))
        comm.send(ip, protocol.pack_month_events(db.get_events_of_calendar(calendar_id, today.month, today.year)))
        for user in current_open_calendars:
            if current_open_calendars[user][0] == calendar_id:
                comm.send(current_users[user], protocol.pack_new_calendar_participant(status, calendar_id, username))
                comm.send((current_users[user], protocol.pack_month_events(db.get_events_of_calendar(calendar_id, current_open_calendars[user][1][:2], current_open_calendars[user][1][3:]))))


if __name__ == '__main__':
    msg_q = queue.Queue()
    comm = ServerComm(4500, msg_q)
    db = data_base()
    opcodes = {"00": handle_login, "01": handle_sign_up, "02": handle_new_calendar, "04": handle_new_event}
    current_users = {} # username: ip
    current_open_calendars = {} # user: [calendar_id, month and year, day]
    while True:
        # handle msgs
        ip, msg = msg_q.get()
        opcode, params = protocol.unpack(msg)
        print(f'got from {ip}: {msg}')
        if opcode in opcodes:
            print(opcodes[opcode](ip, params))
        else:
            print(f'command number {opcode} not in dictionary')
