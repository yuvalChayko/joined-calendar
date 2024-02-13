import sqlite3

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
                " (event_id VARCHAR(4), participant VARCHAR(20), PRIMARY KEY(event_id))",
                "CREATE TABLE IF NOT EXISTS " + self.event_info +
                " (event_id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, calendar_id VARCHAR(3), name VARCHAR(30), manager VARCHAR(20), start_hour VARCHAR(5), end_hour VARCHAR(5), date VARCHAR(10), PRIMARY KEY(event_id))",
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
        #if not self._is_calendar_exists(self.last_calendar_id):
        sql_table = "INSERT INTO " + self.calendars + "(name,manager)  VALUES(?,?)"
        self.db_cursor.execute(sql_table, (name, manager,))
        self.db_conn.commit()
        "add manager to participant table"

        sql = "SELECT calendar_id from " + self.calendars + " ORDER BY calendar_id DESC LIMIT (1)"
        self.db_cursor.execute(sql)
        self.add_calendar_participant(self.db_cursor.fetchone()[0], manager)
        #else:
        #    print("error! calendar already exists")


    def add_calendar_participant(self, id, user):
        """
        if calendar exists, add participant to calendar_participants table
        :param id: str
        :param user: str
        :return: None
        """
        if self._is_calendar_exists(id):

            # check if participant is not already exists
            if not self.is_participant_exists_in_calendar(id, user):

                sql_table = "INSERT INTO " + self.calendars_participants + " VALUES(?,?,?)"
                self.db_cursor.execute(sql_table, (id, user, self.find_color(id),))
                self.db_conn.commit()
            else:
                print("already is a participant")
        else:
            print("calendar do not exists so cant add participant")

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

        for c in self.colors:
            if c not in current_colors:
                return c
        return ""

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
        if self._is_calendar_exists(id) and self._is_user_exists(invited) and self._is_user_exists(invited_by):
            if not self.is_calendar_invitation_exists(id, invited):
                sql_table = "INSERT INTO " + self.calendar_invitations + " VALUES(?,?,?)"
                self.db_cursor.execute(sql_table, (invited, invited_by, id,))
                self.db_conn.commit()
            else:
                print("invitation already exists")
        else:
            print("the calendar doesnt exists so cant add invitation or user not exists")

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

    def add_event(self,name, participants, calendar_id, manager, start, end, date):
        """
        add event to the table and add the invitations to the invitations table if time available
        :param participants: list of participants
        :param calendar_id:
        :param manager:
        :param start:
        :param end:
        :param date:
        :return:
        """

        if self._is_calendar_exists(calendar_id):

            if self.is_participants_in_calendar(participants, calendar_id):
                if self.check_is_time_available(manager, start, end, date):
                    sql = "INSERT INTO " + self.event_info + "(calendar_id, name, manager, start_hour, end_hour, date) VALUES(?,?,?,?,?,?)"
                    self.db_cursor.execute(sql, (calendar_id, name, manager, start, end, date,))
                    self.db_conn.commit()
                    sql = "SELECT event_id from " + self.event_info + " ORDER BY event_id DESC LIMIT (1)"
                    self.db_cursor.execute(sql)
                    self.add_event_participant(self.db_cursor.fetchone()[0], manager)
                else:
                    print("time is not available")
            else:
                print("errorrr event participants are not calendar participants")
        else:
            print("calendar do not exists so cant add event")

    def add_event_participant(self, id, participant):
        """
        add participant to event in events_participants table
        :param id:
        :param participant:
        :return:
        """
        pass

    def is_event_exists(self, id):
        """
        check if event exists
        :param id:
        :return:
        """
        pass

    def is_participant_exists_in_event(self, id, username):
        """
        check if user is a participant in the event
        :param id:
        :param username:
        :return:
        """
        pass

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
        calendar_participants = self.get_calendar_participants(id)
        for x in participants:
            if not x in calendar_participants:
                return False
        return True

    def check_is_time_available(self, username, start, end, date):
        """
        check if the username has free time
        :param username:
        :param start:
        :param end:
        :param date:
        :return: bool
        """

        if self._is_user_exists(username):
            sql = "SELECT start_hour, end_hour FROM " + self.event_info + " WHERE manager = ? AND date = ?"
            self.db_cursor.execute(sql, (username, date,))
            hours = self.db_cursor.fetchall()
            hours = [i for i in hours]
            start = int(start.replace(":", ""))
            end = int(end.replace(":", ""))
            for x in hours:
                if (start >= int(x[0].replace(":", "")) and start < int(x[1].replace(":", ""))) or (end > int(x[0].replace(":", "")) and end <= int(x[1].replace(":", ""))):
                    return False
            return True
        else:
            print("user do not exists so cant check time availability")
            return False


if __name__ == '__main__':
    db = joined_calendar_db()
    print(db.add_user('test1', '1234', "1111111111"))
    print(db.add_calendar("test", "test1"))
    print(db.add_calendar("test", "test1"))
    print(db.add_user('test2', '1234', "2222222222"))
    print(db.add_calendar_participant("1", "test2"))
    print(db.add_calendar_participant("1", "test2"))
    print(db.add_calendar_invitation("1", "test1", "test2"))
    print(db.add_calendar_invitation("1", "test3", "test2"))
    print("here")
    print(db.add_event("test name", ["test1", "test2"], "1", "test1", "14:00", "16:00", "12.2.2024"))


    #print(db.find_color("100"))




