import sqlite3
from datetime import date
import hashlib

class joined_calendar_db:

    def __init__(self):
        self.db_conn = None
        self.db_cursor = None
        self.name_of_db = "joined_calendar_data"
        self.calendars = "calendars"
        self.users = "users"
        self.calendars_participants = "calendars_participants"
        self.events_participants = "events_participants"
        self.event_info = "event_info"
        self.calendar_invitations = "calendar_invitations"
        self.event_invitations = "event_invitations"
        self.reminders = "reminders"
        self.colors = ['BLUE', 'YELLOW', 'RED', 'GREEN', 'PURPLE','PINK', 'GREY', 'ORANGE', 'BROWN', 'GOLD', 'TURQUOISE', 'LIGHT BLUE', 'LIME GREEN', 'SALMON', 'DARK OLIVE GREEN']
        self.joined_color = 'BLACK'
        self.last_event_id = 1000
        self.last_calendar_id = 100

        self._create_db()

    def _create_db(self):
        """
        connect to the db and create the tables that dont exists
        :return: None
        """
        self.db_conn = sqlite3.connect(self.name_of_db)
        self.db_cursor = self.db_conn.cursor()
        sql_table = ["CREATE TABLE IF NOT EXISTS " + self.users +
                "(username VARCHAR(20), password VARCHAR(20), phone_number VARCHAR(10), PRIMARY KEY(username));",
                "CREATE TABLE IF NOT EXISTS " + self.calendars +
                " (calendar_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, name VARCHAR(20), manager VARCHAR(20))",

                "CREATE TABLE IF NOT EXISTS " + self.calendars_participants +
                " (calendar_id VARCHAR(3), participant VARCHAR(20), color VARCHAR(20), PRIMARY KEY(calendar_id, participant))",
                "CREATE TABLE IF NOT EXISTS " + self.events_participants +
                " (event_id VARCHAR(4), participant VARCHAR(20), PRIMARY KEY(event_id, participant))",
                "CREATE TABLE IF NOT EXISTS " + self.event_info +
                " (event_id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, calendar_id VARCHAR(3), name VARCHAR(30), manager VARCHAR(20), start_hour VARCHAR(5), end_hour VARCHAR(5), date VARCHAR(10))",
                "CREATE TABLE IF NOT EXISTS " + self.calendar_invitations +
                " (username VARCHAR(20), invited_by VARCHAR(20), calendar_id VARCHAR(3), PRIMARY KEY(username, invited_by, calendar_id))",
                "CREATE TABLE IF NOT EXISTS " + self.event_invitations +
                " (username VARCHAR(20), invited_by VARCHAR(20), calendar_id VARCHAR(3), event_id VARCHAR(4), PRIMARY KEY(username, invited_by, calendar_id, event_id))",
                "CREATE TABLE IF NOT EXISTS " + self.reminders +
                " (username VARCHAR(20), event_id VARCHAR(4), date VARCHAR(10), time VARCHAR(5), PRIMARY KEY(username, event_id))"]


        [self.db_cursor.execute(x) for x in sql_table]
        self.db_conn.commit()



    def _is_calendar_exists(self, id):
        """
        check if calendar exists
        :param id: str
        :return: bool
        """
        sql_table = "SELECT calendar_id FROM " + self.calendars + " WHERE calendar_id = ?"

        self.db_cursor.execute(sql_table, (id,))
        return self.db_cursor.fetchone() is not None

    def _is_event_exists(self, id):
        """
        check if event exists
        :param id: str
        :return: bool
        """
        sql_table = "SELECT event_id FROM " + self.event_info + " WHERE event_id = ?"

        self.db_cursor.execute(sql_table, (id,))
        return self.db_cursor.fetchone() is not None

    def is_user_exists(self, user):
        """
        check if user exists
        :param user: str
        :return: bool
        """
        sql_table = "SELECT username FROM " + self.users + " WHERE username = ?"

        self.db_cursor.execute(sql_table, (user,))
        return self.db_cursor.fetchone() is not None

    def add_calendar(self, name, manager):
        """
        add calendar to calendars table and calendar_participants table, increase last_calendar_id
        :param name: str
        :param manager: str
        :return: id(str) or empty str if already exists
        """
        sql_table = "INSERT INTO " + self.calendars + "(name,manager)  VALUES(?,?)"
        self.db_cursor.execute(sql_table, (name, manager,))
        self.db_conn.commit()

        "add manager to participant table"

        sql = "SELECT calendar_id from " + self.calendars + " ORDER BY calendar_id DESC LIMIT (1)"
        self.db_cursor.execute(sql)
        id = self.db_cursor.fetchone()[0]
        self.add_calendar_participant(id, manager)
        return id


    def add_calendar_participant(self, id, user):
        """
        if calendar exists, add participant to calendar_participants table
        :param id: str
        :param user: str
        :return:
        """
        flag = False
        if self._is_calendar_exists(id):

            # check if participant is not already exists
            if not self.is_participant_exists_in_calendar(id, user):

                sql_table = "INSERT INTO " + self.calendars_participants + " VALUES(?,?,?)"
                self.db_cursor.execute(sql_table, (id, user, self.find_color(id),))
                self.db_conn.commit()
                flag = True
            else:
                print("already is a participant")
        else:
            print("calendar do not exists so cant add participant")
        return flag

    def find_color(self, id):
        """
        find color that is mot occupied in the calendar
        :param id: str
        :return: color(str) if the calendar is not full
        """
        sql_table = "SELECT color FROM " + self.calendars_participants + " WHERE calendar_id = ?"
        self.db_cursor.execute(sql_table, (id,))
        current_colors = self.db_cursor.fetchall()
        current_colors = [i[0] for i in current_colors]
        color = ""
        for c in self.colors:
            if c not in current_colors:
                color = c
                break
        return color

    def add_user(self, username, password, phone):
        """
        add username to users table if user is not exists
        :param username: str
        :param password: str
        :param phone: str
        :return: if user not exists (bool)
        """

        flag = self.is_user_exists(username)

        if not flag:
            sql_table = "INSERT INTO " + self.users + " VALUES(?,?,?)"
            self.db_cursor.execute(sql_table, (username, hashlib.sha256(password.encode()).digest(), phone,))
            self.db_conn.commit()

        return not flag

    def is_participant_exists_in_calendar(self, id, user):
        """
        check if the user alredy exists in the calendar
        :param id:
        :param user:
        :return:
        """
        sql_table = "SELECT participant FROM " + self.calendars_participants + " WHERE calendar_id = ?"
        self.db_cursor.execute(sql_table, (id,))
        participants = self.db_cursor.fetchall()
        participants = [i[0] for i in participants]

        return user in participants


    def add_calendar_invitation(self, id, invited_by, invited):
        """
        add calendar invitation to the table
        :param id:
        :param invited_by:
        :param invited:
        :return:
        """
        flag = False
        if self._is_calendar_exists(id) and self.is_user_exists(invited) and self.is_user_exists(invited_by):
            if not self.is_calendar_invitation_exists(id, invited):
                sql_table = "INSERT INTO " + self.calendar_invitations + " VALUES(?,?,?)"
                self.db_cursor.execute(sql_table, (invited, invited_by, id,))
                self.db_conn.commit()
                flag = True
            else:
                print("invitation already exists")
        else:
            print("the calendar doesnt exists so cant add invitation or user not exists")
        return flag

    def is_calendar_invitation_exists(self, id, user):
        """
        check if invitation exists in the table
        :param id:
        :param user:
        :return:
        """
        sql_table = "SELECT username FROM " + self.calendar_invitations + " WHERE calendar_id = ?"
        self.db_cursor.execute(sql_table, (id,))
        invitations = self.db_cursor.fetchall()
        invitations = [i[0] for i in invitations]

        return user in invitations

    def add_event(self, name, participants, calendar_id, manager, start, end, date):
        """
        add event to the table and add the invitations to the invitations table if time available
        :param name: str
        :param participants: list of participants
        :param calendar_id:
        :param manager:
        :param start:
        :param end:
        :param date:
        :return:
        """
        event_id = ""
        if self._is_calendar_exists(calendar_id):

            if self.is_participants_in_calendar(participants, calendar_id):
                if self.check_is_time_available(manager, start, end, date):
                    sql = "INSERT INTO " + self.event_info + "(calendar_id, name, manager, start_hour, end_hour, date) VALUES(?,?,?,?,?,?)"
                    self.db_cursor.execute(sql, (calendar_id, name, manager, start, end, date,))
                    self.db_conn.commit()
                    sql = "SELECT event_id from " + self.event_info + " ORDER BY event_id DESC LIMIT (1)"
                    self.db_cursor.execute(sql)
                    event_id = self.db_cursor.fetchone()[0]
                    self.add_event_participant(event_id, manager)
                    participants = participants[1:]
                    for user in participants:
                        self.add_event_invitation(event_id, calendar_id, user, manager)
                else:
                    print("time is not available")
            else:
                print("errorrr event participants are not calendar participants")
        else:
            print("calendar do not exists so cant add event")
        return event_id

    def add_event_participant(self, id, participant):
        """
        add participant to event in events_participants table
        :param id:
        :param participant:
        :return:
        """
        flag = False
        if self._is_event_exists(id):

            # check if participant is not already exists
            if not self.is_participant_exists_in_event(id, participant):

                sql_table = "INSERT INTO " + self.events_participants + " VALUES(?,?)"
                self.db_cursor.execute(sql_table, (id, participant,))
                self.db_conn.commit()
                flag = True
            else:
                print("errorrr already is a participant")
        else:
            print("event do not exists so cant add participant")
        return flag

    def is_participant_exists_in_event(self, id, username):
        """
        check if user is a participant in the event
        :param id:
        :param username:
        :return:
        """
        sql_table = "SELECT participant FROM " + self.events_participants + " WHERE event_id = ?"
        self.db_cursor.execute(sql_table, (id,))
        participants = self.db_cursor.fetchall()
        participants = [i[0] for i in participants]

        return username in participants

    def get_calendar_participants(self, id):
        """
        return calendar participants
        :param id:
        :return: list
        """
        sql = "SELECT participant FROM " + self.calendars_participants + " WHERE calendar_id = ?"
        self.db_cursor.execute(sql, (id,))
        participants = self.db_cursor.fetchall()
        participants = [i[0] for i in participants]
        return participants

    def is_participants_in_calendar(self, participants, id):
        """
        check if the usernames in the list are participants in the calendar
        :param participants:
        :param id:
        :return: bool
        """
        flag = True
        calendar_participants = self.get_calendar_participants(id)
        for x in participants:
            if not x in calendar_participants:
                flag = False
                break
        return flag

    def check_is_time_available(self, username, start, end, date):
        """
        check if the username has free time
        :param username:
        :param start:
        :param end:
        :param date:
        :return: bool
        """
        flag = False
        if self.is_user_exists(username):
            sql = "SELECT start_hour, end_hour FROM " + self.event_info + " WHERE manager = ? AND date = ?"
            self.db_cursor.execute(sql, (username, date,))
            hours = self.db_cursor.fetchall()
            hours = [i for i in hours]
            start = int(start.replace(":", ""))
            end = int(end.replace(":", ""))
            for x in hours:
                if (start >= int(x[0].replace(":", "")) and start < int(x[1].replace(":", ""))) or (end > int(x[0].replace(":", "")) and end <= int(x[1].replace(":", ""))):
                    break
            else:
                flag = True
        else:
            print("user do not exists so cant check time availability")
        return flag

    def add_event_invitation(self, event_id, calendar_id, invited, invited_by):
        """

        :param event_id:
        :param calendar_id:
        :param invited:
        :param invited_by:
        :return:
        """
        flag = False
        if self._is_event_exists(event_id) and self.is_user_exists(invited) and self.is_user_exists(invited_by):
            if not self.is_event_invitation_exists(event_id, invited) and self.is_participant_exists_in_calendar(calendar_id, invited):
                sql_table = "INSERT INTO " + self.event_invitations + " VALUES(?,?,?,?)"
                self.db_cursor.execute(sql_table, (invited, invited_by, calendar_id, event_id,))
                self.db_conn.commit()
                flag = True
            else:
                print("invitation already exists")
        else:
            print("the calendar doesnt exists so cant add invitation or user not exists")
        return flag

    def is_event_invitation_exists(self, event_id, invited):
        """
        check if invitation already exists
        :param event_id:
        :param invited:
        :return:
        """
        sql_table = "SELECT username FROM " + self.event_invitations + " WHERE event_id = ?"
        self.db_cursor.execute(sql_table, (event_id,))
        invitations = self.db_cursor.fetchall()
        invitations = [i[0] for i in invitations]

        return invited in invitations

    def is_manager_calander(self, id, user):
        """
        check if user is manager
        :param id:
        :param user:
        :return:
        """
        sql = "SELECT manager FROM " + self.calendars + " WHERE calendar_id = ?"
        self.db_cursor.execute(sql, (id,))
        manager = self.db_cursor.fetchone()[0]

        return manager == user

    def is_manager_event(self, id, user):
        """
        check if user is manager
        :param id:
        :param user:
        :return:
        """
        sql = "SELECT manager FROM " + self.event_info + " WHERE event_id = ?"
        self.db_cursor.execute(sql, (id,))
        manager = self.db_cursor.fetchone()[0]

        return manager == user

    def get_password(self, username):
        """
        return password
        :param username:
        :return:
        """

        sql = "SELECT password FROM " + self.users + " WHERE username = ?"
        self.db_cursor.execute(sql, (username,))
        password = self.db_cursor.fetchone()[0]
        if password == None:
            password = "-1"
        return password

    def change_calendar_name(self, id, name):
        """
        change the calendar name
        :param id:
        :param name:
        :return:
        """
        sql = "UPDATE " + self.calendars + " SET name = " + name + " WHERE calendar_id = ?"
        self.db_cursor.execute(sql, (id,))
        self.db_conn.commit()


    def change_event_name(self, id, name):
        """
           change the event name
           :param id:
           :param name:
           :return:
           """
        sql = "UPDATE " + self.event_info + " SET name = " + name + " WHERE event_id = ?"
        self.db_cursor.execute(sql, (id,))
        self.db_conn.commit()


    def change_event_time(self, id, start, end, date):
        """
        change event time
        :param id:
        :param start:
        :param end:
        :param date:
        :return:
        """
        sql = "UPDATE " + self.event_info + " SET start_hour = " + start + " , end_hour = " + end + " , date = " + date + " WHERE event_id = ?"
        self.db_cursor.execute(sql, (id,))
        self.db_conn.commit()


    def add_reminder(self, time, date, event_id, username):
        """
        add reminder to reminder table
        :param time:
        :param date:
        :param event_id:
        :param username:
        :return:
        """
        sql_table = "INSERT INTO " + self.reminders + " VALUES(?,?,?,?)"
        self.db_cursor.execute(sql_table, (username, event_id, date, time,))
        self.db_conn.commit()

    def get_today_reminders(self):
        """
        return list of all the reminders at the same day and delete them from the reminders table
        :return: list of all the reminders at the same day
        """
        today = date.today()
        today = today.strftime("%d.%m.%Y")
        sql = "SELECT username, event_id, time FROM " + self.reminders + " WHERE date = ?"
        self.db_cursor.execute(sql, (today,))
        reminders = self.db_cursor.fetchall()
        sql = "DELETE FROM " + self.reminders + " WHERE date = ?"
        self.db_cursor.execute(sql, (today,))
        self.db_conn.commit()


        return reminders

    def delete_reminder_for_user(self, username, event_id):
        """
        delete the reminder from reminders table
        :param username:
        :param event_id:
        :return:
        """
        sql = "DELETE FROM " + self.reminders + " WHERE username = ? And event_id = ?"
        self.db_cursor.execute(sql, (username, event_id,))
        self.db_conn.commit()

    def delete_reminder_for_all(self, event_id):
        """
        delete all reminders for this event from reminders table
        :param event_id:
        :return:
        """
        sql = "DELETE FROM " + self.reminders + " WHERE event_id = ?"
        self.db_cursor.execute(sql, (event_id,))
        self.db_conn.commit()

    def get_event_participants(self, id):
        """
        return event participants
        :param id:
        :return: list
        """
        sql = "SELECT participant FROM " + self.events_participants + " WHERE event_id = ?"
        self.db_cursor.execute(sql, (id,))
        participants = self.db_cursor.fetchall()
        participants = [i[0] for i in participants]
        return participants

    def exit_calendar(self, calendar_id, username):
        """
        remove user from calendar
        :param calendar_id:
        :param username:
        :return:
        """
        if self._is_calendar_exists(calendar_id) and self.is_user_exists(username) and self.is_participant_exists_in_calendar(calendar_id, username):
            if self.is_manager_calander(calendar_id, username):
                # delete calendar
                sql = ["DELETE FROM " + self.calendar_invitations + " WHERE calendar_id = ?",
                       "DELETE FROM " + self.calendars_participants + " WHERE calendar_id = ?",
                       "DELETE FROM " + self.calendars + " WHERE calendar_id = ?"]
                [self.db_cursor.execute(x, (calendar_id,)) for x in sql]
                self.db_conn.commit()

                sql = "SELECT event_id FROM " + self.event_info + " WHERE calendar_id = ?"
                self.db_cursor.execute(sql, (calendar_id,))
                events = self.db_cursor.fetchall()
                events = [x[0] for x in events]
                for x in events:
                    sql = ["DELETE FROM " + self.event_invitations + " WHERE event_id = ?",
                    "DELETE FROM " + self.events_participants + " WHERE event_id = ?",
                    "DELETE FROM " + self.reminders + " WHERE event_id = ?"]
                    [self.db_cursor.execute(s, (x,)) for s in sql]
                    self.db_conn.commit()

                sql = "DELETE FROM " + self.event_info + " WHERE calendar_id = ?"
                self.db_cursor.execute(sql, (calendar_id,))
                self.db_conn.commit()

            else:
                # remove from calendar

                #self.calendars_participants, self.event_info, self.events_participants, self.event_invitations, self.reminders

                sql = "DELETE FROM " + self.calendars_participants + " WHERE calendar_id = ? AND participant = ?"
                self.db_cursor.execute(sql, (calendar_id, username, ))
                self.db_conn.commit()

                sql = "SELECT event_id FROM " + self.event_info + " WHERE calendar_id = ? AND manager = ?"
                self.db_cursor.execute(sql, (calendar_id, username,))
                events = self.db_cursor.fetchall()
                events = [x[0] for x in events]

                for x in events:
                    sql = ["DELETE FROM " + self.events_participants + " WHERE event_id = ? AND participant = ?",
                           "DELETE FROM " + self.reminders + " WHERE event_id = ? AND participant = ?"]
                    [self.db_cursor.execute(s, (x, username,)) for s in sql]
                    self.db_conn.commit()
                    sql = "DELETE FROM " + self.event_invitations + " WHERE event_id = ?"
                    self.db_cursor.execute(sql, (calendar_id,))
                    self.db_conn.commit()

                sql = "DELETE FROM " + self.event_info + " WHERE calendar_id = ? AND manager = ?"
                self.db_cursor.execute(sql, (calendar_id, username,))
                self.db_conn.commit()

    def delete_event(self, event_id, username):
        """
        delete event
        :param event_id:
        :param username:
        :return:
        """
        flag = self.is_manager_event(event_id, username)
        if flag:
            sql = ["DELETE FROM " + self.event_info + " WHERE event_id = ?",
                   "DELETE FROM " + self.event_invitations + " WHERE event_id = ?",
                   "DELETE FROM " + self.events_participants + " WHERE event_id = ?"]
            [self.db_cursor.execute(s, (event_id,)) for s in sql]
            self.db_conn.commit()
        return flag

    def get_manager_calander(self, id):
        """
        get the manager of the calendar
        :param id:
        :return: manager
        """
        sql = "SELECT manager FROM " + self.calendars + " WHERE calendar_id = ?"
        self.db_cursor.execute(sql, (id,))
        manager = self.db_cursor.fetchone()[0]

        return manager

    def get_manager_event(self, id):
        """
        get the manager of the event
        :param id:
        :return: manager
        """
        sql = "SELECT manager FROM " + self.event_info + " WHERE event_id = ?"
        self.db_cursor.execute(sql, (id,))
        manager = self.db_cursor.fetchone()[0]

        return manager

    def get_calendar_invitations(self, username):
        """
        get all the user's calendar invitations
        :param username:
        :return: list of all the invitations
        """

        sql = "SELECT invited_by, calendar_id FROM " + self.calendar_invitations + " WHERE username = ?"
        self.db_cursor.execute(sql, (username,))
        invitations = self.db_cursor.fetchall()
        invitations = [x for x in invitations]
        return invitations

    def get_event_invitations(self, username):
        """
        get all the user's event invitations
        :param username:
        :return: list of all the invitations
        """

        sql = "SELECT invited_by, event_id, calendar_id FROM " + self.event_invitations + " WHERE username = ?"
        self.db_cursor.execute(sql, (username,))
        invitations = self.db_cursor.fetchall()
        invitations = [x for x in invitations]
        return invitations

    def delete_calendar_invitation(self, username, id):
        """
        delete calendar invitation
        :param username:
        :param id:
        :return:
        """
        if self.is_calendar_invitation_exists(id, username):
            sql = "DELETE FROM " + self.calendar_invitations + " WHERE username = ? AND calendar_id = ?"
            self.db_cursor.execute(sql, (username, id,))
            self.db_conn.commit()
        else:
            print("error - calendar invitation doesnt exists")

    def delete_event_invitation(self, username, id):
        """
        delete calendar invitation
        :param username:
        :param id:
        :return:
        """
        if self.is_event_invitation_exists(id, username):
            sql = "DELETE FROM " + self.event_invitations + " WHERE username = ? AND event_id = ?"
            self.db_cursor.execute(sql, (username, id,))
            self.db_conn.commit()
        else:
            print("error - event invitation doesnt exists")

    def get_user_calendars(self, username):
        """
        get list of username calendars ids
        :param username:
        :return:
        """
        sql = "SELECT calendar_id FROM " + self.calendars_participants + " WHERE participant = ?"
        self.db_cursor.execute(sql, (username,))
        calendars = self.db_cursor.fetchall()
        calendars = [x[0] for x in calendars]
        return calendars

    def get_events_of_calendar(self, calendar_id, month, year):
        """
        get list that contains date and color of all the events in this month that users from the calendar are participating
        :param calendar_id:
        :param month:
        :param year:
        :return:
        """
        events = []
        if self._is_calendar_exists(calendar_id):
            participants = self.get_calendar_participants(calendar_id)
            month_year = month + "." + year
            sql = f"SELECT event_id, date FROM {self.event_info} WHERE date LIKE ?"
            wildcard_month_year = '%' + month_year
            self.db_cursor.execute(sql, (wildcard_month_year,))
            temp = self.db_cursor.fetchall()
            ids = []
            dates = []
            set_participants = set(participants)
            for t in temp:
                ids += [t[0]]
                dates += [t[1]]
            print(ids)
            for id in ids:
                p = self.get_event_participants(id)
                set_p = set(p)
                both = set_p & set_participants
                if both:
                    date = dates[ids.index(id)]
                    if len(both) > 1:
                        temp = (date, self.joined_color, [id])
                    else:
                        both = list(both)
                        temp = (date, self.get_color(both[0], calendar_id), [id])

                    for event in events:
                        if event[0] == date:
                            if temp[1] != event[1]:
                                add_id = event[2] + temp[2]
                                events[events.index(event)] = (event[0], self.joined_color, add_id)
                            else:
                                add_id = event[2].append(temp[2])
                                events[events.index(event)] = (event[0], event[1], add_id)

                            break
                    else:
                        events.append(temp)

        return events

    def get_color(self, username, calendar_id):
        """
        get color of username in calendar
        :param username:
        :param calendar_id:
        :return:
        """
        sql = "SELECT color FROM " + self.calendars_participants + " WHERE participant = ? AND calendar_id = ?"
        self.db_cursor.execute(sql, (username, calendar_id,))
        return self.db_cursor.fetchone()[0]

    def get_day_events(self, username, calendar_id, date):
        """
        get event info for all the events of the day
        :param username:
        :param calendar_id:
        :param date:
        :return:
        """
        day, month, year = date.split('.')
        month_event = self.get_events_of_calendar(calendar_id, month, year)
        day_events = None
        if self._is_calendar_exists(calendar_id):
            day_events = []
            for x in month_event:
                if x[0] == date:
                    ids = x[2]
                    for id in ids:
                        day_events += [self.get_event_info(id, username)]
                    break
        return day_events

    def get_calendar_info(self, calendar_id):
        """
        return name and participants
        :param calendar_id:
        :return:
        """

        info = []
        if self._is_calendar_exists(calendar_id):

            participants = self.get_calendar_participants(calendar_id)
            sql = "SELECT name, manager FROM " + self.calendars + " WHERE calendar_id = ?"
            self.db_cursor.execute(sql, (calendar_id,))
            name, manager = self.db_cursor.fetchone()

            info = [name, manager, participants]
        return info

    def get_event_info(self, event_id, username):
        """
        get event info - name, participants, manager, start hour, end hour, date
        :param event_id:
        :param username
        :return:
        """
        info = []
        if self._is_event_exists(event_id):
            participants = self.get_event_participants(event_id)
            if username in participants:
                sql = "SELECT name, start_hour, end_hour, date, manager FROM " + self.event_info + " WHERE event_id = ?"
            else:
                sql = "SELECT start_hour, end_hour, date FROM " + self.event_info + " WHERE event_id = ?"
            self.db_cursor.execute(sql, (event_id,))
            info = self.db_cursor.fetchone()
            info = list(info) + [participants]

        return info

    def get_some_event_info(self, event_id, calendar_id):
        """
        get event color (by participants color) and date
        :param event_id:
        :param calendar_id
        :return:
        """
        info = []
        if self._is_calendar_exists(calendar_id) and self._is_event_exists(event_id):
            participants = self.get_calendar_participants(calendar_id)

            set_participants = set(participants)
            p = self.get_event_participants(event_id)
            set_p = set(p)
            both = set_p & set_participants
            sql = "SELECT date FROM " + self.event_info + " WHERE event_id = ?"
            self.db_cursor.execute(sql, (event_id,))
            date = self.db_cursor.fetchone()[0]
            if both:
                if len(both) > 1:
                    info = (date, self.joined_color)
                else:
                    both = list(both)
                    info = (date, self.get_color(both[0], calendar_id))
        return info


if __name__ == '__main__':
    db = joined_calendar_db()
    print(db.add_user('test1', '1234', "1111111111"))
    print(db.add_calendar("test", "test1"))
    print(db.add_calendar("test", "test1"))
    print(db.add_user('test2', '1234', "2222222222"))
    print(db.add_user('test3', '1234', "3333333333"))
    print(db.add_calendar_participant("1", "test2"))
    print(db.add_calendar_participant("1", "test2"))
    print(db.add_calendar_invitation("1", "test1", "test2"))
    print(db.add_calendar_invitation("2", "test1", "test2"))
    print(db.add_calendar_invitation("1", "fake", "test2"))
    print(db.add_event("test name", ["test1", "test2"], "1", "test1", "14:00", "16:00", "12.02.2024"))
    print(db.add_calendar_participant("2", "test2"))
    print(db.add_event("test name", ["test1", "test2"], "2", "test1", "11:00", "13:00", "12.02.2024"))
    print(db.add_event("test name", ["test1"], "2", "test1", "11:00", "13:00", "13.02.2024"))
    print(db.add_event("test name", ["test1"], "2", "test1", "11:00", "13:00", "13.03.2024"))
    print(db.add_event("test name", ["test1", "test2"], "1", "test1", "08:00", "09:00", "12.02.2024"))
    print(db.add_event_participant("1", "test1"))
    print(db.add_event_participant("1", "test2"))
    print(db.add_event_participant("700", "test3"))
    db.add_reminder("18:00", "15.02.2024", '1', "test1")
    db.add_reminder("17:00", "15.02.2024", '1', "test2")
    db.add_reminder("18:00", "15.03.2024", '2', "test1")
    db.add_reminder("18:00", "15.03.2024", '2', "test2")
    db.delete_reminder_for_user("test2", "2")
    db.delete_reminder_for_user("test1", "2")
    db.delete_reminder_for_all("2")

    print(db.get_today_reminders())
    print(db.get_calendar_invitations("test2"))
    print(db.get_event_invitations("test2"))
    db.delete_calendar_invitation("test2", '1')
    db.delete_event_invitation("test2", '1')
    print(db.get_calendar_invitations("test2"))
    print(db.get_event_invitations("test2"))
    print(db.get_user_calendars("test1"))
    print(db.delete_event("2", "test1"))
    print(db.get_events_of_calendar("2", "02", "2024"))
    print(db.get_day_events("test2", "1", "12.02.2024"))
    print(db.get_calendar_info("1"))
    print(db.get_some_event_info("5", "1"))
    print(db.get_some_event_info("1", "1"))

    #print(db.find_color("100"))


