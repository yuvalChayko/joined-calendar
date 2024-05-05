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
        ids = db.get_user_calendars(username)
        msgs_to_send += [protocol.pack_calendar_ids(ids)]
        data = [ids[0]] + db.get_calendar_info(ids[0])
        msgs_to_send += [protocol.pack_new_calendar("9", data)]
        today = datetime.now()
        current_open_calendars[username] = [ids[0], str(today.month).zfill(2)+"."+str(today.year)]  # user: [calendar_id, month and year]
        print("hereeeeeeeee")
        msgs_to_send += [protocol.pack_month_events(db.get_events_of_calendar(ids[0], today.month, today.year))]

        if db.get_calendar_invitations(username) or db.get_event_invitations(username):
            msgs_to_send += [protocol.pack_there_is_an_invitation()]
        current_users[username] = ip
    comm.send(ip, protocol.pack_login(status))
    for msg in msgs_to_send:
        comm.send(ip, msg)


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
    msgs_to_send = []
    if not db.is_user_exists(username):
        status = 0

        db.add_user(username, password, phone_number)
        db.add_calendar("personal", username)
        ids = db.get_user_calendars(username)
        msgs_to_send += [protocol.pack_calendar_ids(ids)]
        data = [ids[0]] + db.get_calendar_info(ids[0])
        msgs_to_send += [protocol.pack_new_calendar("9", data)]
        today = datetime.now()
        current_open_calendars[username] = [ids[0], str(today.month).zfill(2)+"."+str(today.year)]  # user: [calendar_id, month and year]
        msgs_to_send += [protocol.pack_month_events(db.get_events_of_calendar(ids[0], today.month, today.year))]
        current_users[username] = ip
    comm.send(ip, protocol.pack_sign_up(status))
    for msg in msgs_to_send:
        comm.send(ip, msg)

def handle_new_calendar(ip, params):
    """
    check if every participant is an existing user and if so, create the calendar and add invitations. send status if succeed. if succeed send id and if not send why
    :param ip:
    :param params: name, participants
    :return:
    """
    username = [i for i in current_users if current_users[i] == ip][0]
    name, participants = params
    participants = participants.split("^")
    not_existing_participants = [i for i in participants if not db.is_user_exists(i)]
    if not not_existing_participants:
        id = db.add_calendar(name, username)
        comm.send(ip, protocol.pack_new_calendar("0", [id, name, username, [username]]))
        today = datetime.now()
        current_open_calendars[username] = [id, str(today.month).zfill(2)+"."+str(today.year)]  # user: [calendar_id, month and year]
        comm.send(ip, protocol.pack_month_events(db.get_events_of_calendar(id, today.month, today.year)))
        for i in participants:
            db.add_calendar_invitation(id, username, i)
            if i in current_users:
                comm.send(current_users[i], protocol.pack_there_is_an_invitation())
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
                    comm.send(current_users[p], protocol.pack_there_is_an_invitation())
            date, color = get_event_info(date, calendar_id)
            comm.send(ip, protocol.pack_event_info(date, color))
            for user in current_open_calendars:
                month = date[3:]
                if month == current_open_calendars[user][1] and db.is_participant_exists_in_calendar(current_open_calendars[user][0], username) and user != username:
                    print("username", user)
                    date, color = get_event_info(event_id, current_open_calendars[user][0])
                    comm.send(current_users[user], protocol.pack_event_info(date, color))

        else:
            comm.send(ip, protocol.pack_new_event("1", ""))


def get_event_info(date, calendar_id):
    """
    return the color of the event, the id and the date.
    :param date:
    :param calendar_id:
    :return:
    """
    return db.get_day_color(date, calendar_id)


def handle_calendar_invitation(ip, params):
    """
    if calendar exists, invited_by is manager, username exists and not already in calendar or invitation already exists, add invitation to table and if username is in current_users send him the invitation
    :param params: calendar_id, username, invited_by
    :return:
    """
    calendar_id, username = params
    invited_by = [i for i in current_users if current_users[i] == ip][0]
    if not db._is_calendar_exists(calendar_id):
        comm.send(ip, protocol.pack_is_calendar_invitation_work("1"))
    elif not db.is_manager_calander(calendar_id, invited_by):
        comm.send(ip, protocol.pack_is_calendar_invitation_work("2"))
    elif not db.is_user_exists(username):
        comm.send(ip, protocol.pack_is_calendar_invitation_work("3"))
    elif db.is_participant_exists_in_calendar(calendar_id, username):
        comm.send(ip, protocol.pack_is_calendar_invitation_work("4"))
    elif db.is_calendar_invitation_exists(calendar_id, username):
        comm.send(ip, protocol.pack_is_calendar_invitation_work("5"))
    else:
        comm.send(ip, protocol.pack_is_calendar_invitation_work("0"))
        db.add_calendar_invitation(calendar_id, invited_by, username)
        if username in current_users.keys():
            comm.send(current_users[username], protocol.pack_there_is_an_invitation())


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
        # today = datetime.now()
        info = db.get_calendar_info(calendar_id)
        comm.send(ip, protocol.pack_new_calendar(status, [calendar_id, info[0], info[1], info[2]]))
        today = datetime.now()
        current_open_calendars[username] = [calendar_id, str(today.month).zfill(2)+"."+str(today.year)]  # user: [calendar_id, month and year]
        # comm.send(ip, protocol.pack_month_events(db.get_events_of_calendar(calendar_id, today.month, today.year)))
        for user in current_open_calendars:
            if current_open_calendars[user][0] == calendar_id:
                if user != username:
                    comm.send(current_users[user], protocol.pack_new_calendar_participant(status, calendar_id, username))
                print(f"open {current_open_calendars}")
                print(user)
                comm.send(current_users[user], protocol.pack_month_events(db.get_events_of_calendar(calendar_id, current_open_calendars[user][1][:2], current_open_calendars[user][1][3:])))

def handle_event_invitation(ip, params):
    """
    check if username is manager and if username, calendar and event exist and if username is participant in the calendar and if invitation not already exists and username not already participant.
    if so, add invitation to table and if username in current usernames, send the invitation.
    :param ip:
    :param params: calendar_id, event_id, username
    :return:
    """

    calendar_id, event_id, username = params
    invited_by = [i for i in current_users if current_users[i] == ip][0]
    if not db._is_calendar_exists(calendar_id):
        comm.send(ip, protocol.pack_event_invitation_succeed("1"))
    elif not db.is_manager_event(event_id, invited_by):
        comm.send(ip, protocol.pack_event_invitation_succeed("2"))
    elif not db.is_user_exists(username):
        comm.send(ip, protocol.pack_event_invitation_succeed("3"))
    elif not db.is_participant_exists_in_calendar(calendar_id, username):
        comm.send(ip, protocol.pack_event_invitation_succeed("4"))
    elif db.is_event_invitation_exists(event_id, username):
        comm.send(ip, protocol.pack_event_invitation_succeed("5"))
    elif db.is_participant_exists_in_event(event_id, username):
        comm.send(ip, protocol.pack_event_invitation_succeed("6"))
    else:
        comm.send(ip, protocol.pack_event_invitation_succeed("0"))
        db.add_event_invitation(event_id, calendar_id, username, invited_by)
        if username in current_users.keys():
            comm.send(current_users[username],
                      protocol.pack_there_is_an_invitation())


def handle_is_event_accepted(ip, params):
    """
    if accepted - add participant to table, send event to user, send users that are currently looking on the calendar the new color, remove invitation
    if declined - remove invitation from table
    :param ip:
    :param params: status, event_id
    :return:
    """
    status, event_id = params
    username = [i for i in current_users if current_users[i] == ip][0]
    db.delete_event_invitation(username, event_id)
    if status == "0":
        db.add_event_participant(event_id, username)
        calendar_id = db.get_calendar_from_event(event_id)
        date = db.get_event_date(event_id)
        info = db.get_day_color(date, calendar_id)
        if len(info) > 0:
            for user in current_open_calendars:
                if current_open_calendars[user][1] == info[0][3:] and db.is_participant_exists_in_calendar(current_open_calendars[0], username):
                    date, color = db.get_day_color(date, current_open_calendars[user][0])
                    comm.send(current_users[user], protocol.pack_event_info(date, color))


def handle_change_name_of_calendar(ip, params):
    """
    if manager - change the name of the calendar on the table.
    send new name for users who currently watch the calendar
    :param ip:
    :param params: calendar_id, name
    :return:
    """
    calendar_id, name = params
    username = [i for i in current_users if current_users[i] == ip][0]
    if db.is_manager_calander(calendar_id, username):
        db.change_calendar_name(calendar_id, name)
        comm.send(ip, protocol.pack_calendar_name_edit("0", calendar_id, name))
        for user in current_open_calendars:
            if current_open_calendars[user][0] == calendar_id:
                comm.send(current_users[user], protocol.pack_calendar_name_edit("0", calendar_id, name))
    else:
        comm.send(ip, protocol.pack_calendar_name_edit("1", calendar_id, ""))


def handle_change_name_of_event(ip, params):
    """
    if manager - change the name of the calendar on the table.
    send new name for users who currently watch the calendar
    :param ip:
    :param params: calendar_id, name
    :return:
    """
    event_id, name = params
    calendar_id = db.get_calendar_from_event(event_id)
    username = [i for i in current_users if current_users[i] == ip][0]
    if db.is_manager_event(event_id, username):
        db.change_event_name(event_id, name)
        comm.send(ip, protocol.pack_event_name_edit("0", event_id, name))
    else:
        comm.send(ip, protocol.pack_event_name_edit("1", event_id, ""))


def handle_time_change(ip, params):
    """
    if all participants are free and user is manager - change time in table
    if not, send why couldnt change
    :param ip:
    :param params: event_id, start, end, date
    :return:
    """
    event_id, start, end, date = params
    username = [i for i in current_users if current_users[i] == ip][0]
    if db._is_event_exists(event_id):
        calendar_id = db.get_calendar_from_event(event_id)
        participants = db.get_event_participants(event_id)
        users_do_not_free = []
        for p in participants:
            if not db.check_is_time_available(p, start, end, date) and db.events_in_time(p, start, end, date) != [event_id]:
                users_do_not_free.append(p)
        if len(users_do_not_free) > 0:
            comm.send(ip, protocol.pack_time_edit("1", calendar_id, event_id, users_do_not_free))
        elif not db.is_manager_event(event_id, username):
            comm.send(ip, protocol.pack_time_edit("2", calendar_id, event_id, []))
        else:
            old_date = db.get_event_date(event_id)
            db.change_event_time(event_id, start, end, date)
            if date != old_date:
                participants = set(participants)
                for user in current_users:
                    if current_users[user][1] == date[3:]:
                        p = set(db.get_calendar_participants(calendar_id))
                        both = list(p & participants)
                        if len(both) > 0:
                            date, color = db.get_day_color(date, calendar_id)
                            comm.send(current_users[user], protocol.pack_event_info(date, color))
                    if current_users[user][1] == old_date[3:]:
                        p = set(db.get_calendar_participants(calendar_id))
                        both = list(p & participants)
                        if len(both) > 0:
                            old_date_and_color = db.get_day_color(old_date, calendar_id)
                            if len(old_date_and_color) > 0:
                                old_date, color = old_date_and_color
                                comm.send(current_users[user], protocol.pack_event_info(old_date, color))
                            else:
                                comm.send(current_users[user], protocol.pack_event_info(old_date, ""))

            comm.send(ip, protocol.pack_time_edit("0", calendar_id, event_id, [start, end, date]))
    else:
        comm.send(ip, protocol.pack_time_edit("3", "", event_id, []))


def handle_delete_event(ip, params):
    """
    delete event from table and send it to the users who are currently looking on the month of the event and the event is on their calendar
    :param params: event_id
    :return:
    """
    event_id = params[0]
    username = [i for i in current_users if current_users[i] == ip][0]
    if db._is_event_exists(event_id) and db.is_manager_event(event_id, username):
        date_of_event = db.get_event_date(event_id)
        month_year = date_of_event[3:]
        participants = set(db.get_event_participants(event_id))
        db.delete_event(event_id, username)
        comm.send(ip, protocol.pack_event_dalete("0", event_id))
        for user in current_users:
            if current_users[user][1] == month_year:
                calendar_id = current_users[user][0]
                p = set(db.get_calendar_participants(calendar_id))
                both = list(p & participants)
                if len(both) > 0:
                    info = db.get_some_event_info(event_id, calendar_id)
                    if len(info) > 0:
                        date, color = info
                    else:
                        date = date_of_event
                        color = ""
                    comm.send(current_users[user], protocol.pack_event_info(date, color))

    elif db._is_event_exists(event_id) and not db.is_manager_event(event_id, username):
        comm.send(ip, protocol.pack_event_dalete("1", event_id))
    else:
        comm.send(ip, protocol.pack_event_dalete("2", event_id))


def handle_get_invitations(ip, params):
    """
    send calendar's and event's invitations to user
    :param ip:
    :param params:
    :return:
    """
    username = [i for i in current_users if current_users[i] == ip][0]
    comm.send(ip, protocol.pack_invitations(db.get_calendar_invitations(username) + db.get_event_invitations(username)))


def handle_exit_calendar(ip, params):
    """
    if calendar exist:
            if username is manager - delete calendar and all its participants, delete events that were created in the calendar and tell the clients who are on the calendar that it was deleted
            otherwise - delete participant from table, delete participant from events that were created in the calendar and if he is their manager - deletes them
                        send the users that are currently on the calendar that the participant has exit
            in both cases - if the user that exits is manager of some events so they get deleted - send users who are currently on a calendar that some of its participants are in the calendar that someone exits
                            otherwise and if user is participant in some events on the calendar - send users who are currently on a calendar that the user that exits the calendar was in is a participant there.
    otherwise - tell the user why couldnt exit
    :param params: calendar_id
    :return:
    """
    calendar_id = params[0]
    username = [i for i in current_users if current_users[i] == ip][0]
    info = db.get_calendar_info(calendar_id)
    status = db.exit_calendar(calendar_id, username)
    if status == 4:
        comm.send(ip, protocol.pack_delete_calendar("1", calendar_id))
    else:
        name, manager, participants = info

        if status == 3:
            comm.send(ip, protocol.pack_delete_calendar("0", calendar_id))
            personal_id = db.get_personal_calendar(username)
            info = [personal_id, "personal", username, [username]]
            comm.send(ip, protocol.pack_new_calendar("0", info))
            today = datetime.now()
            current_open_calendars[username] = [personal_id, str(today.month).zfill(2) + "." + str(today.year)]  # user: [calendar_id, month and year]

            comm.send(ip, protocol.pack_month_events(db.get_events_of_calendar(personal_id, today.month, today.year)))
            for user in current_users:
                if current_open_calendars[user][0] == calendar_id:
                    comm.send(current_users[user], protocol.pack_exit_calendar(calendar_id, username))
                    comm.send(current_users[user], protocol.pack_month_events(
                        db.get_events_of_calendar(current_open_calendars[user][0], current_open_calendars[user][1][:2],
                                                  current_open_calendars[user][1][3:])))
                else:
                    # p = set(db.get_calendar_participants(calendar_id))
                    # both = list(p & set(participants))
                    # if len(both) > 0:
                    comm.send(current_users[user], protocol.pack_month_events(db.get_events_of_calendar(current_open_calendars[user][0], current_open_calendars[user][1][:2], current_open_calendars[user][1][3:])))

        elif status == 2:
            comm.send(ip, protocol.pack_delete_calendar("0", calendar_id))
            today = datetime.now()
            personal_id = db.get_personal_calendar(username)
            info = [personal_id, "personal", username, [username]]
            comm.send(ip, protocol.pack_new_calendar("0", info))
            today = datetime.now()
            current_open_calendars[username] = [personal_id, str(today.month).zfill(2) + "." + str(today.year)]  # user: [calendar_id, month and year]
            comm.send(ip, protocol.pack_month_events(db.get_events_of_calendar(personal_id, today.month, today.year)))
            for user in current_users:
                if current_open_calendars[user][0] == calendar_id:
                    comm.send(current_users[user], protocol.pack_exit_calendar(calendar_id, username))
                    comm.send(current_users[user], protocol.pack_month_events(
                        db.get_events_of_calendar(current_open_calendars[user][0], current_open_calendars[user][1][:2],
                                                  current_open_calendars[user][1][3:])))
                else:
                    if username in db.get_calendar_participants(current_open_calendars[user][0]):
                        comm.send(current_users[user], protocol.pack_month_events(
                            db.get_events_of_calendar(current_open_calendars[user][0], current_open_calendars[user][1][:2],
                                                      current_open_calendars[user][1][3:])))
        else:
            today = datetime.now()
            for user in current_users:
                if user in participants:
                    comm.send(current_users[user], protocol.pack_delete_calendar("0", calendar_id))
                    if current_open_calendars[user][0] == calendar_id:
                        personal_id = db.get_personal_calendar(user)
                        info = [personal_id, "personal", user, [user]]
                        comm.send(current_users[user], protocol.pack_new_calendar("0", info))
                        today = datetime.now()
                        current_open_calendars[user] = [personal_id, str(today.month).zfill(2) + "." + str(today.year)]  # user: [calendar_id, month and year]
                        comm.send(current_users[user], protocol.pack_month_events(
                            db.get_events_of_calendar(personal_id, today.month, today.year)))
                else:
                    # participants = set(participants)
                    # p = set(db.get_calendar_participants(calendar_id))
                    # both = list(p & participants)
                    # if len(both) > 0:
                    comm.send(current_users[user], protocol.pack_month_events(
                        db.get_events_of_calendar(current_open_calendars[user][0], current_open_calendars[user][1][:2],
                                                  current_open_calendars[user][1][3:])))


def handle_calendar_ids(ip, params):
    """
    if user exists, send him his calendar ids
    :param params:
    :return:
    """
    username = [i for i in current_users if current_users[i] == ip][0]
    comm.send(ip, protocol.pack_calendar_ids(db.get_user_calendars(username)))


def handle_day_events(ip, params):
    """

    :param ip:
    :param params: calendar_id, date
    :return:
    """
    calendar_id, date = params
    username = [i for i in current_users if current_users[i] == ip][0]
    comm.send(ip, protocol.pack_day_events(db.get_day_events(username, calendar_id, date)))


def handle_month_events(ip, params):
    """
    get month events of calendar (color and date)
    :param ip:
    :param params: calendar_id, month, year
    :return:
    """
    username = [i for i in current_users if current_users[i] == ip][0]
    calendar_id, month, year = params

    current_open_calendars[username] = [calendar_id,
                                        str(month).zfill(2) + "." + str(year)]  # user: [calendar_id, month and year]

    comm.send(ip, protocol.pack_month_events(db.get_events_of_calendar(calendar_id, month, year)))


def handle_get_calendar_info(ip, params):
    """
    get calendar info and send to user
    :param ip:
    :param params:
    :return:
    """
    username = [i for i in current_users if current_users[i] == ip][0]
    info = db.get_calendar_info(params[0])
    if info != []:
        data = [params[0]] + db.get_calendar_info(params[0])
        comm.send(ip, protocol.pack_new_calendar("9", data))
        today = datetime.now()
        current_open_calendars[username] = [params[0], str(today.month).zfill(2) + "." + str(today.year)]  # user: [calendar_id, month and year]
        comm.send(ip, protocol.pack_month_events(db.get_events_of_calendar(params[0], today.month, today.year)))


def disconnect_client(ip, params):
    """
    delete ip from current_users and user from current_open_calendars
    :param ip:
    :param params:
    :return:
    """
    # username = next(filter(lambda item: item[1] == ip, current_users.items()), None)[0]
    username = [i for i in current_users if current_users[i] == ip]
    if len(username) != 0:
        username = username[0]
        del current_users[username]
        if username in current_open_calendars:
            del current_open_calendars[username]





if __name__ == '__main__':
    msg_q = queue.Queue()
    comm = ServerComm(4500, msg_q)
    db = data_base()
    opcodes = {"00": handle_login, "01": handle_sign_up, "02": handle_new_calendar, "04": handle_new_event,
               "10": handle_calendar_invitation, "11": handle_is_calendar_accepted, "12": handle_event_invitation,
               "13": handle_is_event_accepted, "14": handle_get_invitations, "20": handle_change_name_of_calendar,
               "21": handle_change_name_of_event, "22": handle_time_change, "30": handle_delete_event,
               "31": handle_exit_calendar, "40": handle_calendar_ids, "41": handle_day_events, "42": handle_month_events,
               "43": handle_get_calendar_info, "99": disconnect_client}
    current_users = {} # username: ip
    current_open_calendars = {} # user: [calendar_id, month and year, day]
    #current_open_calendars["test1"] = ["2", "03.2024", "02"]
    while True:
        # handle msgs
        ip, msg = msg_q.get()
        opcode, params = protocol.unpack(msg)
        print(f'got from {ip}: {msg}')
        if opcode in opcodes:
            print(opcodes[opcode](ip, params))
        else:
            print(f'command number {opcode} not in dictionary')
