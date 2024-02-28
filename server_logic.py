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
    elif username in current_users.values():
        status = 3
    else:
        msgs_to_send += [db.get_user_calendars(username)]
        msgs_to_send += [db.get_calendar_invitations(username).append(db.get_event_invitations(username))]
    comm.send(ip, protocol.pack_login(status))
    if len(msgs_to_send) != 0:
        comm.send(ip, protocol.pack_calendar_ids(msgs_to_send[0]))
        comm.send(ip, protocol.pack_invitations(msgs_to_send[1]))

def handle_sign_up(ip, params):
    """
    try to open a username and return msg if available or if taken. if available, add user and add him a private calendar and send it to him
    :param ip:
    :param params: username, password, phone
    :return:
    """
    username, password, phone_number = params
    status = 1
    msgs_to_send = []
    if not db.is_user_exists(username):
        status = 0

        db.add_calendar("personal", username)
        comm.send(ip, protocol.pack_calendar_ids(db.get_user_calendars(username)))


if __name__ == '__main__':
    msg_q = queue.Queue()
    comm = ServerComm(4500, msg_q)
    db = data_base()
    opcodes = {"00": handle_login, "01": handle_sign_up}
    current_users = {} # ip: username
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














