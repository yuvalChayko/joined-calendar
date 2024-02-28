from client_comm import ClientComm
import queue
import client_protocol as protocol

def handle_login(params):
    """
    show if and why couldnt log in
    :param params: status
    :return:
    """
    msg = "succeed"
    if params[0] == "1":
        msg = "incorrect password"
    elif params[0] == "2":
        msg = "incorrect username"
    elif params[0] == 3:
        msg = "username already open on other computer"
    return msg

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
    msg = "succeed"
    if params[0] == "1":
        msg = "username already taken"


    return msg

def sign_up(username, password, phone_number):
    """
    try to sign up
    :param username:
    :param password:
    :param phone_number:
    :return:
    """
    comm.send(protocol.pack_signup(username, password, phone_number))


if __name__ == '__main__':
    msg_q = queue.Queue()
    comm = ClientComm('127.0.0.1', 4500, msg_q)
    opcodes = {"00": handle_login, "01": handle_sign_up}
    month_event = []
    current_calendar = ""
    current_month = ""
    current_day = ""
    user_calendars = []
    while True:
        login("test1", "1234")
        sign_up("test1", "1234", "4444444444")
        msg = msg_q.get()
        opcode, params = protocol.unpack(msg)
        print(f'got from server: {msg}')
        if opcode in opcodes:
            print(opcodes[opcode](params))
        else:
            print(f'command number {opcode} not in dictionary')