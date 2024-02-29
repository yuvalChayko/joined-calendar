from server_comm import ServerComm
import queue
import server_protocol as protocol
from joined_calendar_db import joined_calendar_db as data_base
import hashlib

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
        comm.send(ip, protocol.pack_new_calendar("0", id))
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
    not_existing_participants = list(set(not_existing_participants) & set(not_in_calendar))
    if not_existing_participants:
        comm.send(ip, protocol.pack_new_event("1", not_existing_participants))
    else:
        if not db.check_is_time_available(username, start, end, date):
            event_id = db.add_event(name, participants, calendar_id, username, start, end, date)
            comm.send(ip, protocol.pack_new_event("0", event_id))
            for p in participants:
                db.add_event_invitation(event_id, calendar_id, p, username)
                if p in current_users:
                    comm.send(current_users[p], protocol.pack_event_invitation(calendar_id, event_id, name, username, start, end, date))
            color = db.get_some_event_info(event_id, calendar_id)[0]
            comm.send(ip, protocol.pack_event_info(event_id, date, color))
            for user in current_open_calendars:
                month = date[3:]
                if month == current_open_calendars[user][1] and db.is_participant_exists_in_calendar(current_open_calendars[user][0]):
                    date, color = db.get_some_event_info(event_id, current_open_calendars[user][0])
                    comm.send(current_users[user], protocol.pack_event_info(event_id, date, color))

        else:
            comm.send(ip, protocol.pack_new_event("1", ""))


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
