import sqlite3
from datetime import date

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

    def _is_user_exists(self, user):
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
        :return: None
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

        flag = self._is_user_exists(username)

        if not flag:
            sql_table = "INSERT INTO " + self.users + " VALUES(?,?,?)"
            self.db_cursor.execute(sql_table, (username, hash(password), phone,))
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
        if self._is_calendar_exists(id) and self._is_user_exists(invited) and self._is_user_exists(invited_by):
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

    def is_event_exists(self, id):
        """
        check if event exists
        :param id:
        :return:
        """
        sql = "SELECT event_id FROM " + self.event_info + " WHERE event_id = ?"

        self.db_cursor.execute(sql, (id,))
        return self.db_cursor.fetchone() is not None

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
        if self._is_user_exists(username):
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
        if self._is_event_exists(event_id) and self._is_user_exists(invited) and self._is_user_exists(invited_by):
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
        self.db_cursor.execute(sql_table, (id,))
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
        manager = self.db_cursor.fetchone()

        return manager == user

    def is_manager_event(self, id, user):
        """
        check if user is manager
        :param id:
        :param user:
        :return:
        """
        sql = "SELECT manager FROM " + self.events_participants + " WHERE event_id = ?"
        self.db_cursor.execute(sql, (id,))
        manager = self.db_cursor.fetchone()

        return manager == user

    def get_password(self, username):
        """
        return password
        :param username:
        :return:
        """

        sql = "SELECT password FROM " + self.users + " WHERE username = ?"
        self.db_cursor.execute(sql, (username,))
        password = self.db_cursor.fetchone()
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

    def change_event_name(self, id, name):
        """
           change the event name
           :param id:
           :param name:
           :return:
           """
        sql = "UPDATE " + self.event_info + " SET name = " + name + " WHERE event_id = ?"
        self.db_cursor.execute(sql, (id,))

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

    def set_today_reminders(self):
        """
        return list of all the reminders at the same day and delete them from the reminders table
        :return: list of all the reminders at the same day
        """
        today = date.today()
        today = today.strftime("%d.%m.%Y")
        print(today)



if __name__ == '__main__':
    db = joined_calendar_db()
    print(db.add_user('test1', '1234', "1111111111"))
    print(db.add_calendar("test", "test1"))
    print(db.add_calendar("test", "test1"))
    print(db.add_user('test2', '1234', "2222222222"))
    print(db.add_calendar_participant("1", "test2"))
    print(db.add_calendar_participant("1", "test2"))
    print(db.add_calendar_invitation("1", "test1", "test2"))
    print(db.add_calendar_invitation("1", "fake", "test2"))
    print(db.add_event("test name", ["test1", "test2"], "1", "test1", "14:00", "16:00", "12.2.2024"))
    print(db.add_event_participant("1", "test1"))
    print(db.add_event_participant("1", "test2"))
    print(db.add_event_participant("700", "test3"))
    db.set_today_reminders()

    #print(db.find_color("100"))




