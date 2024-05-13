import wx
from pubsub import pub
import wx.adv
import wx.lib.scrolledpanel
import time
from datetime import datetime


from wx.lib.calendar import Calendar
from wx.adv import CalendarCtrl, GenericCalendarCtrl, CalendarDateAttr

class MyFrame(wx.Frame):
    def __init__(self, graphics_q, parent=None):
        super(MyFrame, self).__init__(parent, title="joined calendar", size=(900, 700))
        self.SetMinSize(self.GetSize())
        self.SetMaxSize(self.GetSize())
        self.graphics_q = graphics_q
        # create status bar
        self.CreateStatusBar(1)

        # create main panel - to put on the others panels
        main_panel = MainPanel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(main_panel, 1, wx.EXPAND)

        # arrange the frame
        self.SetSizer(box)
        self.Layout()
        self.Show()


        

class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        pub.subscribe(self.show_error_notification, "error")
        pub.subscribe(self.show_calendar, "show calendar")
        pub.subscribe(self.show_invitation, "show invitation")
        pub.subscribe(self.mark_dates, "mark")
        pub.subscribe(self.unmark_dates, "unmark")
        pub.subscribe(self.hide_panel, "hide")
        pub.subscribe(self.show_day, "show day")
        pub.subscribe(self.color_invitation, "new invitation")
        self.frame = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.v_box = wx.BoxSizer(wx.VERTICAL)
        # create object for each panel
        self.login = LoginPanel(self, self.frame)
        self.first = FirstPanel(self, self.frame)
        self.registration = RegistrationPanel(self, self.frame)
        self.calendar = CalendarPanel(self, self.frame)
        self.new_cal = newCalendarPanel(self, self.frame)
        self.event = EventPanel(self, self.frame)
        self.new_cal_parti = newCalendarParticipantPanel(self, self.frame)
        self.new_evt_parti = newEventParticipantPanel(self, self.frame)
        self.cal_name = calNamePanel(self, self.frame)
        self.evt_name = evtNamePanel(self, self.frame)
        self.new_event = newEventPanel(self, self.frame)
        self.evt_time = evtTimePanel(self, self.frame)
        self.invitations = invitationsPanel(self, self.frame)
        self.v_box.Add(self.login, 1, wx.EXPAND)
        self.v_box.Add(self.registration, 1, wx.EXPAND)
        self.v_box.Add(self.calendar, 1, wx.EXPAND)
        self.v_box.Add(self.first, 1, wx.EXPAND)
        self.v_box.Add(self.event, 1, wx.EXPAND)
        self.v_box.Add(self.new_cal, 1, wx.EXPAND)
        self.v_box.Add(self.new_cal_parti, 1, wx.EXPAND)
        self.v_box.Add(self.new_evt_parti, 1, wx.EXPAND)
        self.v_box.Add(self.invitations, 1, wx.EXPAND)
        self.v_box.Add(self.new_event, 1, wx.EXPAND)
        self.v_box.Add(self.cal_name, 1, wx.EXPAND)
        self.v_box.Add(self.evt_name, 1, wx.EXPAND)
        self.v_box.Add(self.evt_time, 1, wx.EXPAND)


        # The first panel to show
        self.SetSizer(self.v_box)
        self.Layout()
        self.first.Show()



    def show_error_notification(self, error):
        """
        show notification
        :return:
        """
        wx.MessageBox(error, "Error", wx.OK | wx.ICON_ERROR)


    def show_calendar(self, name, manager, participants):
        """
        show calendar
        :param name:
        :param manager:
        :param participants:
        :return:
        """
        # self.calendar.change_calendar(name, manager, participants)
        self.v_box.Detach(self.calendar)
        self.calendar = CalendarPanel(self, self.frame, name, participants, manager)
        self.v_box.Add(self.calendar, 1, wx.EXPAND)
        # print("here")
        # print(name)
        # self.SetSizerAndFit(self.v_box)
        self.SetSizer(self.v_box)
        self.frame.SetStatusText("Red is the joined color")
        self.calendar.Show()

    def show_invitation(self, params):
        """
        show invitations
        :param params: name, manager, start, end, date, participants, id or name, manager, participants, id
        :return:
        """
        print(f"in invitations {params}")
        self.v_box.Detach(self.invitations)
        if len(params) == 7:
            self.invitations = invitationsPanel(self, self.frame, params[0], params[2], params[1], params[3], params[4], params[5])
        elif len(params) == 4:
            self.invitations = invitationsPanel(self, self.frame, name=params[0], manager=params[1], participants=params[-2])
        else:
            self.invitations = invitationsPanel(self, self.frame)
        self.v_box.Add(self.invitations, 1, wx.EXPAND)
        self.SetSizer(self.v_box)
        self.invitations.Show()

    def hide_panel(self, panel):
        """
        hide panel
        :param panel:
        :return:
        """
        if panel == "login":
            self.login.Hide()
        elif panel == "register":
            self.registration.Hide()
        elif panel == "calendar":
            self.frame.SetStatusText("")
            self.calendar.Hide()
        elif panel == "event":
            self.event.Hide()
        elif panel == "new cal":
            self.frame.SetStatusText("")
            self.new_cal.Hide()
        elif panel == "new cal parti":
            self.frame.SetStatusText("")
            self.new_cal_parti.Hide()
            self.frame.SetStatusText("Red is the joined color")
            self.calendar.Show()
        elif panel == "invitation":
            self.invitations.Hide()
        elif panel == "new evt parti":
            self.frame.SetStatusText("")
            self.new_evt_parti.Hide()
            self.event.Show()
        elif panel == "new event":
            self.frame.SetStatusText("Red is the joined color")
            self.new_event.Hide()
            self.calendar.Show()
        elif panel == "cal name":
            self.cal_name.Hide()
        elif panel == "evt name":
            self.evt_name.Hide()
        elif panel == "evt time":
            self.evt_time.Hide()

    def mark_dates(self, dates):
        """
        mark dates with events
        :param dates:
        :return:
        """
        print("in parent", dates)
        self.calendar.mark_dates(dates)


    def unmark_dates(self, dates):
        """
        unmark dates with events
        :param dates:
        :return:
        """
        self.calendar.unmark_dates(dates)


    def show_day(self, event):
        """
        show day events
        :param events:
        :return:
        """
        print(f"here {event}")
        self.v_box.Detach(self.event)
        self.event.events = event # [id, date, name, start, end, manager, [participants]]
        if type(event) is list and len(event) == 7:
            self.event = EventPanel(self, self.frame, event[1], event[0], event[-2], event[-3], event[2], event[3])
        elif type(event) is list and len(event) == 5:
            self.event = EventPanel(self, self.frame, participants=event[0], start=event[1], end=event[2], date=event[3])
        else:
            self.event = EventPanel(self, self.frame, date=event)

        self.v_box.Add(self.event, 1, wx.EXPAND)
        # print("here")
        # print(name)
        # self.SetSizerAndFit(self.v_box)
        self.SetSizer(self.v_box)
        self.event.Show()
        # else:
        #     self.v_box.Detach(self.no_events)
        #     self.no_events = NoEventsPanel(self, self.frame, event[0])
        #     self.v_box.Add(self.no_events, 1, wx.EXPAND)
        #     self.SetSizer(self.v_box)
        #     self.no_events.Show()


    def show_new_event(self, date):
        self.v_box.Detach(self.new_event)
        self.new_event = newEventPanel(self, self.frame, date)
        self.v_box.Add(self.new_event, 1, wx.EXPAND)
        self.SetSizer(self.v_box)
        self.frame.SetStatusText("participants names must be separated with ', '")
        self.new_event.Show()

    def color_invitation(self):
        self.calendar.invitationBtn.SetForegroundColour(wx.GREEN)
        self.Refresh()

    def uncolor_invitation(self):
        self.calendar.invitationBtn.SetForegroundColour(wx.BLACK)
        self.Refresh()


class LoginPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=frame.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        title = wx.StaticText(self,-1, label="Login")
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)

        smallfont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        # username
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        nameText = wx.StaticText(self, 1, label="Username: ")
        nameText.SetFont(smallfont)
        self.nameField = wx.TextCtrl(self, -1, name="username", size=(300, 50))
        self.nameField.SetFont(smallfont)
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)
        # password
        passBox = wx.BoxSizer(wx.HORIZONTAL)
        passText = wx.StaticText(self, 1, label="Password: ")
        passText.SetFont(smallfont)
        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size=(300, 50))
        self.passField.SetFont(smallfont)
        passBox.Add(passText, 0, wx.ALL, 5)
        passBox.Add(self.passField, 0,  wx.ALL, 5)
        # login & registration buttons
        login = wx.Image("pics\\done.png")
        login.Rescale(250, 100)
        back = wx.Image("pics\\back.png")
        back.Rescale(200, 80)
        back = wx.Bitmap(back)
        login = wx.Bitmap(login)
        logBtn = wx.BitmapButton(self,
                                 size=(200, 80), name="button", bitmap=login)
        logBtn.SetBackgroundColour(wx.LIGHT_GREY)
        logBtn.SetWindowStyleFlag(wx.NO_BORDER)
        backBtn = wx.BitmapButton(self,
                                  size=(200, 80), name="button", bitmap=back)
        backBtn.SetBackgroundColour(wx.LIGHT_GREY)
        backBtn.SetWindowStyleFlag(wx.NO_BORDER)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        # backBtn = wx.Button(self, wx.ID_ANY, label="Back", size=(200, 80))
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(40)
        # registerBtn = wx.Button(self, wx.ID_ANY, label="register", size=(200, 80))
        logBtn.Bind(wx.EVT_BUTTON, self.handle_login)
        btnBox.Add(logBtn, 0, wx.ALL, 5)
        # btnBox = wx.BoxSizer(wx.HORIZONTAL)
        # backBtn = wx.Button(self, wx.ID_ANY, label="Back", size=(200, 80))
        # backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        # btnBox.Add(backBtn, 1, wx.ALL, 5)
        # btnBox.AddSpacer(40)
        # loginBtn = wx.Button(self, wx.ID_ANY, label="login", size=(200, 80))
        # loginBtn.Bind(wx.EVT_BUTTON, self.handle_login)
        # btnBox.Add(loginBtn, 0, wx.ALL, 5)
        # add all elements to sizer
        sizer.AddSpacer(40)
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(60)
        sizer.Add(nameBox,0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(20)
        sizer.Add(passBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(30)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)


        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()



    def handle_login(self, event):
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        if not username or not password :
            self.frame.SetStatusText("Must enter name and password")
        else:
            # self.frame.SetStatusText("waiting for Server approve")
            self.frame.graphics_q.put(("login", (username, password)))

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.first.Show()

class RegistrationPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=frame.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        title = wx.StaticText(self, -1, label="Register")
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        # username
        smallfont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        nameText = wx.StaticText(self, 1, label="Username: ")
        nameText.SetForegroundColour(wx.BLACK)
        nameText.SetFont(smallfont)
        self.nameField = wx.TextCtrl(self, -1, name="username", size=(300,50))
        self.nameField.SetFont(smallfont)
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)
        # password
        passBox = wx.BoxSizer(wx.HORIZONTAL)
        passText = wx.StaticText(self, 1, label="Password: ")
        passText.SetForegroundColour(wx.BLACK)
        passText.SetFont(smallfont)
        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size=(300, 50))
        self.passField.SetFont(smallfont)
        passBox.Add(passText, 0, wx.ALL, 5)
        passBox.Add(self.passField, 0,  wx.ALL, 5)
        # phone number
        phoneBox = wx.BoxSizer(wx.HORIZONTAL)
        phoneText = wx.StaticText(self, 1, label="Phone:      ")
        phoneText.SetForegroundColour(wx.BLACK)
        phoneText.SetFont(smallfont)
        self.phoneField = wx.TextCtrl(self, -1, name="Phone", size=(300, 50))
        self.phoneField.SetFont(smallfont)
        phoneBox.Add(phoneText, 0, wx.ALL, 5)
        phoneBox.Add(self.phoneField, 0,  wx.ALL, 5)
        # login & registration buttons
        register = wx.Image("pics\\done.png")
        register.Rescale(250, 100)
        back = wx.Image("pics\\back.png")
        back.Rescale(200, 80)
        back = wx.Bitmap(back)
        register = wx.Bitmap(register)
        regBtn = wx.BitmapButton(self,
                                       size=(200, 80),  name="button", bitmap=register)
        regBtn.SetBackgroundColour(wx.LIGHT_GREY)
        regBtn.SetWindowStyleFlag(wx.NO_BORDER)
        backBtn = wx.BitmapButton(self,
                                        size=(200, 80),  name="button", bitmap=back)
        backBtn.SetBackgroundColour(wx.LIGHT_GREY)
        backBtn.SetWindowStyleFlag(wx.NO_BORDER)


        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        # backBtn = wx.Button(self, wx.ID_ANY, label="Back", size=(200, 80))
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(40)
        # registerBtn = wx.Button(self, wx.ID_ANY, label="register", size=(200, 80))
        regBtn.Bind(wx.EVT_BUTTON, self.handle_registration)
        btnBox.Add(regBtn, 0, wx.ALL, 5)
        # add all elements to sizer
        sizer.AddSpacer(40)
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(60)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(20)

        sizer.Add(passBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(20)

        sizer.Add(phoneBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(30)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)


        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()


    def handle_registration(self, event):
        username = self.nameField.GetValue()
        password = self.passField.GetValue()
        phone = self.phoneField.GetValue()
        if not username or not password or not phone:
            self.frame.SetStatusText("Must enter name, password and phone")
        else:
            # self.frame.SetStatusText("waiting for Server approve")
            self.frame.graphics_q.put(("register", (username, password, phone)))

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.first.Show()


class FirstPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=frame.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        title = wx.StaticText(self, -1, label="joined calendar")
        titlefont = wx.Font(50, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        # login & registration buttons
        btnfont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        loginBtn = wx.Button(self, wx.ID_ANY, label="login", size=(300, 300))
        loginBtn.SetFont(btnfont)
        loginBtn.Bind(wx.EVT_BUTTON, self.handle_login)
        btnBox.Add(loginBtn, 0, wx.ALL, 5)
        btnBox.AddSpacer(50)
        # add all elements to sizer
        sizer.AddSpacer(50)
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(100)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        regBtn = wx.Button(self, wx.ID_ANY, label="register", size=(300, 300))
        regBtn.SetFont(btnfont)
        regBtn.Bind(wx.EVT_BUTTON, self.handle_reg)
        btnBox.Add(regBtn, 1, wx.ALL, 5)

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_login(self, event):
        self.frame.SetStatusText('')
        self.Hide()
        self.parent.login.Show()

    def handle_reg(self, event):
        self.frame.SetStatusText('')
        self.Hide()                                                                         
        self.parent.registration.Show()


class CalendarPanel(wx.Panel):
    def __init__(self, parent, frame, name="personal", participants=None, manager="1"):
        wx.Panel.__init__(self, parent, pos=parent.GetPosition(), size=parent.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.events = []

        self.title_row = wx.BoxSizer(wx.HORIZONTAL)
        # title
        self.title = wx.StaticText(self, -1, label=name)
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        calfont = wx.Font(35, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.title.SetForegroundColour(wx.BLACK)
        self.title.SetFont(titlefont)
        #arrrow button
        left = wx.Image("pics\\left.png")
        left.Rescale(100, 80)
        right = wx.Image("pics\\right.png")
        right.Rescale(100, 80)
        left = wx.Bitmap(left)
        right = wx.Bitmap(right)
        # create button at point (20, 20)
        self.leftBtn = wx.BitmapButton(self,
                            size=(100, 80), pos=(100,50), name="button", bitmap=left)
        self.leftBtn.SetBackgroundColour(wx.LIGHT_GREY)
        self.leftBtn.SetWindowStyleFlag(wx.NO_BORDER)
        self.rightBtn = wx.BitmapButton(self,
                                       size=(100, 80), pos=(660, 50), name="button", bitmap=right)
        self.rightBtn.SetBackgroundColour(wx.LIGHT_GREY)
        self.rightBtn.SetWindowStyleFlag(wx.NO_BORDER)
        self.leftBtn.Bind(wx.EVT_BUTTON, self.left_cal)
        self.rightBtn.Bind(wx.EVT_BUTTON, self.right_cal)

        # set bmp as bitmap for button
        #self.leftBtn.SetBitmap(left)
        #self.rightBtn.SetBitmap(right)
        self.title_row.Add(self.leftBtn, 1, wx.ALL, 5)
        self.title_row.Add(self.rightBtn, 1, wx.ALL, 5)
        btnBox2 = wx.BoxSizer(wx.HORIZONTAL)
        changeBtn = wx.Button(self, wx.ID_ANY, label="change name", size=(100, 40), pos=(765,95))
        changeBtn.Bind(wx.EVT_BUTTON, self.change_calendar_name)
        btnBox2.Add(changeBtn, 0, wx.ALL, 5)
        addBtn = wx.Button(self, wx.ID_ANY, label="add participant", size=(100, 40), pos=(765,50))
        addBtn.Bind(wx.EVT_BUTTON, self.add_calendar_participant)
        btnBox2.Add(addBtn, 0, wx.ALL, 5)



        self.title_row.Add(self.title, 1, wx.ALL, 5)
        self.title_row.Add(btnBox2, 0, wx.ALL, 5)




        # participants = ["1", "2", "3"]
        # p_text = wx.StaticText(self, -1, "participants: ", pos = (430, 30))
        # p = wx.Choice(self, -1, pos = (450, 30), choices=participants)

        self.mainbox = wx.BoxSizer(wx.VERTICAL)

        # self.newBtn = wx.Button(self, wx.ID_ANY, label="new calendar", size=(100, 40), pos=(400, 0))
        # self.newBtn.Bind(wx.EVT_BUTTON, self.new_calendar)
        #
        # mainbox.AddSpacer(20)
        # mainbox.Add(self.newBtn, 0, wx.ALL, 5)
        #
        # # button
        # self.partBtn = wx.Button(self, wx.ID_ANY, label="participants", size=(100, 40), pos=(10,0))
        # self.partBtn.Bind(wx.EVT_BUTTON, self.display)
        #

        self.btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.partBtn = wx.Button(self, wx.ID_ANY, label="participants", size=(100, 40))
        self.partBtn.Bind(wx.EVT_BUTTON, self.display)
        self.btnBox.Add(self.partBtn, 1, wx.ALL, 5)
        self.invitationBtn = wx.Button(self, wx.ID_ANY, label="invitations", size=(100, 40))
        self.invitationBtn.Bind(wx.EVT_BUTTON, self.show_invitations)
        self.btnBox.Add(self.invitationBtn, 1, wx.ALL, 5)
        self.newBtn = wx.Button(self, wx.ID_ANY, label="New calendar", size=(100, 40))
        self.newBtn.Bind(wx.EVT_BUTTON, self.new_calendar)
        self.btnBox.Add(self.newBtn, 1, wx.ALL, 5)
        self.btnBox.AddSpacer(430)
        delBtn = wx.Button(self, wx.ID_ANY, label="Exit calendar", size=(100, 40))
        delBtn.Bind(wx.EVT_BUTTON, self.exit_calendar)
        self.btnBox.Add(delBtn, 0, wx.ALL, 5)
        self.myScrolled = ParticipantsPanel(self, self.frame,self.partBtn, participants)


        self.mainbox.Add(self.btnBox)

        self.mainbox.AddSpacer(20)
        # mainbox.Add(self.partBtn,  0, wx.ALL, 5)


        self.mainbox.Add(self.title, 0, wx.CENTER)


        calSizer =  wx.BoxSizer(wx.VERTICAL)

        # self.cal = CalendarCtrl(self, 0, wx.DateTime().Today(),
        #                             size=(800,800) ,name="cal-1")


        self.cal = GenericCalendarCtrl(self, -1, wx.DateTime().Today(),
                                   style = wx.adv.CAL_SUNDAY_FIRST
                                        | wx.adv.CAL_SEQUENTIAL_MONTH_SELECTION,name="cal-2",size=(720,450))
        # self.cal.SetHolidayColours(wx.BLUE, wx.BLUE)
        # self.cal.SetHoliday(21)
        # self.cal.SetHolidayColours(wx.GREEN, wx.GREEN)
        # self.cal.SetHoliday(22)

        # self.cal.SetAttr(21, wx.adv.CalendarDateAttr(colBack='green'))
        # self.cal.SetAttr(22, wx.adv.CalendarDateAttr(colBack='blue'))
        # self.cal.ResetAttr(21)
        self.cal.SetFont(calfont)



        #self.cal.SetBackgroundColour(wx.LIGHT_GREY)


        # self.cal = Calendar(self, pos=(20,20), size=(900,800))
        # self.cal.ShowWeekEnd()
        #
        # year = self.cal.GetYear()
        # month = self.cal.GetMonth()


        self.OnChangeMonth()
        # bind some event handlers to each calendar
        self.cal.Bind(wx.adv.EVT_CALENDAR, self.OnCalSelected)
        self.cal.Bind(wx.adv.EVT_CALENDAR_MONTH, self.OnChangeMonth)
        self.cal.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED, self.OnCalSelChanged)
        self.cal.Bind(wx.adv.EVT_CALENDAR_WEEKDAY_CLICKED, self.OnCalWeekdayClicked)
        today = datetime.now()
        self.current_month = str(today.month).zfill(2)

        # create some sizers for layout
        #fgs = wx.FlexGridSizer(cols=2, hgap=50, vgap=50)


        # txt = wx.StaticText(self, -1, "Calendar-1")
        # v_box.Add(txt)
        self.mainbox.AddSpacer(20)
        self.mainbox.Add(self.cal,0, wx.ALL | wx.CENTER,5)



        #box = wx.BoxSizer()
        #box.Add(fgs, 1, wx.EXPAND | wx.ALL, 25)

        #mainbox.Add(calSizer, 1, wx.EXPAND)

        self.frame.SetStatusText("Red is the joined color")
        self.SetSizer(self.mainbox)
        # arrange the screen
        # self.SetSizer(sizer)
        self.Layout()
        self.Hide()



    # def change_calendar(self, name, manager, participants):
    #     """
    #     change calendar on screen
    #     :param name:
    #     :param manager:
    #     :param participants:
    #     :return:
    #     """


    def OnCalSelected(self, evt):
        print('OnCalSelected: %s\n' % evt.Date)
        # if evt.Date.month == wx.DateTime.Aug and evt.Date.day == 14:
        #     print("HAPPY BIRTHDAY!")

        cal = evt.GetEventObject()
        print('name: %s\n' % cal.GetName())

    def OnCalWeekdayClicked(self, evt):
        print('OnCalWeekdayClicked: %s\n' % evt.GetWeekDay())

        cal = evt.GetEventObject()
        print('name: %s\n' % cal.GetName())

    def OnCalSelChanged(self, evt):
        cal = evt.GetEventObject()
        # print("OnCalSelChanged:\n\t%s: %s\n\t%s: %s" %
        #                ("EventObject", cal.__class__,
        #                 "Date       ", cal.GetDate(),
        #                 ))
        # print('name: %s\n' % cal.GetName())
        month = str(cal.GetDate())[4:7]
        monthes = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_num = str(monthes.index(month) + 1).zfill(2)
        year = str(cal.GetDate())[-4:]
        print(month_num)
        print(self.current_month)
        if month_num != self.current_month:  # month change
            self.current_month = month_num
            self.frame.graphics_q.put(("month", (month_num, year)))
        else:  # day sellected
            day = str(cal.GetDate())[8:10]
            day = day.replace(" ", "0")
            self.frame.graphics_q.put(("day", (day+"."+month_num+"."+year)))
            self.Hide()



    def OnChangeMonth(self, evt=None):
        if evt is None:
            cal = self.cal
        else:
            cal = evt.GetEventObject()
        # print('OnChangeMonth: %s\n' % cal.GetDate())
        # cur_month = cal.GetDate().GetMonth() + 1   # convert wxDateTime 0-11 => 1-12
        # for month, day in self.events:
        #     if month == cur_month:
        #         cal.SetHoliday(day)

    def display(self, evt):
        self.partBtn.Hide()
        self.myScrolled.Show()

    def new_calendar(self, evt):
        print("open add new calendar panel")
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.new_cal.Show()
        self.frame.SetStatusText("participants names must be separated with ', '")



    def left_cal(self, evt):
        print("scroll to left cal")
        self.frame.graphics_q.put(("left", ()))

    def right_cal(self, evt):
        print("scroll to right cal")
        self.frame.graphics_q.put(("right", ()))


    def change_calendar_name(self, evt):
        print("try to change calendar name")
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.cal_name.Show()

    def add_calendar_participant(self, evt):
        print("try to add participant to calendar")
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.new_cal_parti.Show()
        self.frame.SetStatusText("participants names must be separated with ', '")


    def show_invitations(self, evt):
        print("show invitations")
        self.frame.graphics_q.put(("invitations", ()))

    def exit_calendar(self, evt):
        print("exit calendar")
        self.frame.graphics_q.put(("exit cal", ()))


    def mark_dates(self, dates):
        print(f"mark in calendar {dates}")
        for i in dates:
            self.cal.SetAttr(i[0], wx.adv.CalendarDateAttr(colBack=i[1]))
        #self.SetSizer(self.mainbox)
        #self.Layout()

        #self.Hide()
        #self.Show()

        self.Refresh()

    def unmark_dates(self, dates):
        for i in dates:
            self.cal.ResetAttr(i)
        self.Layout()




class ParticipantsPanel(wx.Panel):
    def __init__(self, parent, frame, btn, participants):
        wx.Panel.__init__(self, parent,size=(100,140),pos=(0,0))
        self.frame = frame
        self.parent = parent
        if participants:
            self.participants = participants
        else:
            self.participants = ["1", "2", "3"]
        self.participantsBTN = btn

        self.main_box = wx.BoxSizer(wx.VERTICAL)


        # title
        title = wx.StaticText(self, -1, label="participants")
        titlefont = wx.Font(15, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)


        self.main_box.Add(title, 0, wx.LEFT)




        self.scrollP = wx.lib.scrolledpanel.ScrolledPanel(self,-1,style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER, size=(100,80))
        self.scrollP.SetAutoLayout(1)
        self.scrollP.SetupScrolling()

        self.main_box.Add(self.scrollP,0, wx.EXPAND)


        # button
        self.closeBtn = wx.Button(self, wx.ID_ANY, label="close", size=(100, 20))
        self.closeBtn.Bind(wx.EVT_BUTTON, self.close)

        self.display_participants()

        # self.main_box.AddSpacer(20)
        # self.main_box.Add(self.closeBtn,  1, wx.ALL, 5)





        self.SetSizer(self.main_box)

        self.Hide()




    def close(self, evt):
        print("in close")
        self.Hide()
        self.participantsBTN.Show()


    def display_participants(self):
        self.spSizer = wx.BoxSizer(wx.VERTICAL)
        if self.participants != ["1", "2", "3"]:
            for parti in self.participants:
                print("parti", parti)
                user = wx.TextCtrl(self.scrollP, value=parti[0])
                user.SetForegroundColour(parti[1])
                self.spSizer.Add(user)
            self.scrollP.SetSizer(self.spSizer)

        if self.closeBtn:
            self.closeBtn.Destroy()


        self.closeBtn = wx.Button(self, wx.ID_ANY, label="close", size=(100, 20))
        self.closeBtn.Bind(wx.EVT_BUTTON, self.close)
        self.main_box.Add(self.closeBtn, 0, wx.ALL, 5)


        self.SetSizer(self.main_box)
        self.Layout()


class EventPanel(wx.Panel):
    def __init__(self, parent, frame, name="&&&", participants=None, manager="$$$", date="01.01.2024", start = "16:00", end="18:00"):
        wx.Panel.__init__(self, parent, pos=parent.GetPosition(), size=parent.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.events = []
        self.date = date
        mainbox = wx.BoxSizer(wx.VERTICAL)
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.backBtn = wx.Button(self, wx.ID_ANY, label="back", size=(100, 40))
        self.backBtn.Bind(wx.EVT_BUTTON, self.go_back)
        btnBox.Add(self.backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(650)
        newBtn = wx.Button(self, wx.ID_ANY, label="new event", size=(100, 40))
        newBtn.Bind(wx.EVT_BUTTON, self.new_event)
        btnBox.Add(newBtn, 0, wx.ALL, 5)
        mainbox.AddSpacer(10)
        mainbox.Add(btnBox)
        if participants:
            title_row = wx.BoxSizer(wx.HORIZONTAL)
            # title
            title = wx.StaticText(self, -1, label=date)
            titlefont = wx.Font(45, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
            eventfont = wx.Font(25, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
            smallTitleFont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
            title.SetForegroundColour(wx.BLACK)
            title.SetFont(titlefont)
            #arrrow button
            left = wx.Image("pics\\left.png")
            left.Rescale(100, 80)
            right = wx.Image("pics\\right.png")
            right.Rescale(100, 80)
            left = wx.Bitmap(left)
            right = wx.Bitmap(right)
            # create button at point (20, 20)
            self.leftBtn = wx.BitmapButton(self,
                                size=(100, 80), pos=(100,50), name="button", bitmap=left)
            self.leftBtn.SetBackgroundColour(wx.LIGHT_GREY)
            self.leftBtn.SetWindowStyleFlag(wx.NO_BORDER)
            self.rightBtn = wx.BitmapButton(self,
                                           size=(100, 80), pos=(660, 50), name="button", bitmap=right)
            self.rightBtn.SetBackgroundColour(wx.LIGHT_GREY)
            self.rightBtn.SetWindowStyleFlag(wx.NO_BORDER)
            self.leftBtn.Bind(wx.EVT_BUTTON, self.left_event)
            self.rightBtn.Bind(wx.EVT_BUTTON, self.right_event)

            # set bmp as bitmap for button
            title_row.Add(self.leftBtn, 1, wx.ALL, 5)
            title_row.AddSpacer(200)
            title_row.Add(title, 1, wx.ALL, 5)
            title_row.AddSpacer(200)
            title_row.Add(self.rightBtn, 1, wx.ALL, 5)

            if manager != "&&&" and name != "&&&":
                manager_row = wx.BoxSizer(wx.HORIZONTAL)
                manager = wx.StaticText(self, -1, label=manager)
                manager.SetForegroundColour(wx.BLACK)
                manager.SetFont(eventfont)
                manager_title = wx.StaticText(self, -1, label="Manager:   ")
                manager_title.SetForegroundColour(wx.BLACK)
                manager_title.SetFont(smallTitleFont)
                manager_row.Add(manager_title)
                manager_row.Add(manager)
                name_row = wx.BoxSizer(wx.HORIZONTAL)
                name = wx.StaticText(self, -1, label=name)
                name.SetForegroundColour(wx.BLACK)
                name.SetFont(eventfont)
                name_title = wx.StaticText(self, -1, label="Name:   ")
                name_title.SetForegroundColour(wx.BLACK)
                name_title.SetFont(smallTitleFont)
                name_row.Add(name_title)
                name_row.Add(name)
            participants_str = ", ".join(participants)
            participants_row = wx.BoxSizer(wx.HORIZONTAL)
            parti = wx.StaticText(self, -1, label=participants_str)
            parti.SetForegroundColour(wx.BLACK)
            parti.SetFont(eventfont)
            parti_title = wx.StaticText(self, -1, label="Participants:   ")
            parti_title.SetForegroundColour(wx.BLACK)
            parti_title.SetFont(smallTitleFont)
            participants_row.Add(parti_title)
            participants_row.Add(parti)
            time_str = start + " - " + end
            time_row = wx.BoxSizer(wx.HORIZONTAL)
            time = wx.StaticText(self, -1, label=time_str)
            time.SetForegroundColour(wx.BLACK)
            time.SetFont(eventfont)
            time_title = wx.StaticText(self, -1, label="Time:   ")
            time_title.SetForegroundColour(wx.BLACK)
            time_title.SetFont(smallTitleFont)
            time_row.Add(time_title)
            time_row.Add(time)

            buttons = wx.BoxSizer(wx.HORIZONTAL)
            self.editTimeBtn = wx.Button(self, wx.ID_ANY, label="change time", size=(100, 40))
            self.editTimeBtn.Bind(wx.EVT_BUTTON, self.change_time)
            buttons.Add(self.editTimeBtn, 1, wx.ALL, 5)
            buttons.AddSpacer(10)
            editNameBtn = wx.Button(self, wx.ID_ANY, label="change name", size=(100, 40))
            editNameBtn.Bind(wx.EVT_BUTTON, self.change_name)
            buttons.Add(editNameBtn, 0, wx.ALL, 5)
            buttons.AddSpacer(10)
            delBtn = wx.Button(self, wx.ID_ANY, label="delete event", size=(100, 40))
            delBtn.Bind(wx.EVT_BUTTON, self.del_event)
            buttons.Add(delBtn, 0, wx.ALL, 5)
            buttons.AddSpacer(10)
            addBtn = wx.Button(self, wx.ID_ANY, label="Add participants", size=(100, 40))
            addBtn.Bind(wx.EVT_BUTTON, self.add_evt_parti)
            buttons.Add(addBtn, 0, wx.ALL, 5)

            mainbox.AddSpacer(40)
            mainbox.Add(title_row, 0, wx.CENTER)
            if manager != "&&&" and name != "&&&":
                mainbox.AddSpacer(40)
                mainbox.Add(name_row, 0, wx.CENTER)
                mainbox.AddSpacer(20)
                mainbox.Add(participants_row, 0, wx.CENTER)
                mainbox.AddSpacer(20)
                mainbox.Add(time_row, 0, wx.CENTER)
                mainbox.AddSpacer(20)
                mainbox.Add(manager_row, 0, wx.CENTER)
                mainbox.AddSpacer(50)
            else:
                mainbox.AddSpacer(50)
                mainbox.Add(participants_row, 0, wx.CENTER)
                mainbox.AddSpacer(30)
                mainbox.Add(time_row, 0, wx.CENTER)
                mainbox.AddSpacer(60)

            mainbox.Add(buttons, 0, wx.CENTER)

        else:
            # title
            print("hereeeee")
            print(date)
            words = wx.BoxSizer(wx.VERTICAL)
            title = wx.StaticText(self, -1, label="There are no events on")
            titlefont = wx.Font(45, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
            title.SetForegroundColour(wx.BLACK)
            title.SetFont(titlefont)
            date = wx.StaticText(self, -1, label=date)
            date.SetForegroundColour(wx.BLACK)
            date.SetFont(titlefont)
            words.Add(title, 0, wx.CENTER)
            words.AddSpacer(30)
            words.Add(date, 0, wx.CENTER)
            mainbox.AddSpacer(200)
            mainbox.Add(words, 1, wx.CENTER)

        self.SetSizer(mainbox)
        self.Layout()
        self.Hide()


    def left_event(self, evt):
        print("scroll to left event")
        self.frame.graphics_q.put(("left event", ()))

    def right_event(self, evt):
        print("scroll to right event")
        self.frame.graphics_q.put(("right event", ()))

    def go_back(self, evt):
        self.Hide()
        self.frame.SetStatusText("Red is the joined color")
        self.parent.calendar.Show()

    def new_event(self, evt):
        print("new event")
        self.Hide()
        self.frame.SetStatusText("participants names must be separated with ', '")
        self.parent.show_new_event(self.date)


    def del_event(self, evt):
        self.frame.graphics_q.put(("del evt", ()))

    def change_name(self, evt):
        self.Hide()
        self.parent.evt_name.Show()

    def change_time(self, evt):
        self.Hide()
        self.parent.evt_time.Show()

    def add_evt_parti(self, evt):
        self.Hide()
        self.frame.SetStatusText("participants names must be separated with ', '")
        self.parent.new_evt_parti.Show()


class newCalendarPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=frame.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        title = wx.StaticText(self, -1, label="New calendar")
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)

        smallfont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        # name
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        nameText = wx.StaticText(self, 1, label="Name of calendar: ")
        nameText.SetFont(smallfont)
        self.nameField = wx.TextCtrl(self, -1, name="name", size=(300, 50))
        self.nameField.SetFont(smallfont)
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)
        # participants
        partiBox = wx.BoxSizer(wx.HORIZONTAL)
        partiText = wx.StaticText(self, 1, label="Participants to add: ")
        partiText.SetFont(smallfont)
        self.partiField = wx.TextCtrl(self, -1, name="participants", size=(300, 50))
        self.partiField.SetFont(smallfont)
        partiBox.Add(partiText, 0, wx.ALL, 5)
        partiBox.Add(self.partiField, 0, wx.ALL, 5)

        newC = wx.Image("pics\\done.png")
        newC.Rescale(250, 100)
        back = wx.Image("pics\\back.png")
        back.Rescale(200, 80)
        back = wx.Bitmap(back)
        newC = wx.Bitmap(newC)
        newBtn = wx.BitmapButton(self,
                                 size=(200, 80), name="button", bitmap=newC)
        newBtn.SetBackgroundColour(wx.LIGHT_GREY)
        newBtn.SetWindowStyleFlag(wx.NO_BORDER)
        backBtn = wx.BitmapButton(self,
                                  size=(200, 80), name="button", bitmap=back)
        backBtn.SetBackgroundColour(wx.LIGHT_GREY)
        backBtn.SetWindowStyleFlag(wx.NO_BORDER)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(40)
        newBtn.Bind(wx.EVT_BUTTON, self.handle_new_calendar)
        btnBox.Add(newBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.AddSpacer(40)
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(60)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(20)
        sizer.Add(partiBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(30)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)
        self.frame.SetStatusText("participants names must be separated with ', '")

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_new_calendar(self, event):
        name = self.nameField.GetValue()
        participants = self.partiField.GetValue()
        if not name or not participants:
            self.frame.SetStatusText("Must enter name and participants")
        else:
            participants = participants.split(", ")
            self.frame.graphics_q.put(("new cal", (name, participants)))

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.frame.SetStatusText("Red is the joined color")
        self.parent.calendar.Show()


class newCalendarParticipantPanel(wx.Panel):
    def __init__(self, parent, frame, calendar_name="personal"):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=frame.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        title_row = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, -1, label=calendar_name)
        title.SetForegroundColour(wx.BLACK)
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        titleStart = wx.StaticText(self, -1, label="Add participants to ")
        titleStart.SetForegroundColour(wx.BLACK)
        titleStart.SetFont(titlefont)
        title_row.Add(titleStart)
        title_row.Add(title)
        smallfont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        # participants
        partiBox = wx.BoxSizer(wx.HORIZONTAL)
        partiText = wx.StaticText(self, 1, label="Participants to add: ")
        partiText.SetFont(smallfont)
        self.partiField = wx.TextCtrl(self, -1, name="participants", size=(300, 50))
        self.partiField.SetFont(smallfont)
        partiBox.Add(partiText, 0, wx.ALL, 5)
        partiBox.Add(self.partiField, 0, wx.ALL, 5)

        newP = wx.Image("pics\\done.png")
        newP.Rescale(250, 100)
        back = wx.Image("pics\\back.png")
        back.Rescale(200, 80)
        back = wx.Bitmap(back)
        newP = wx.Bitmap(newP)
        newBtn = wx.BitmapButton(self,
                                 size=(200, 80), name="button", bitmap=newP)
        newBtn.SetBackgroundColour(wx.LIGHT_GREY)
        newBtn.SetWindowStyleFlag(wx.NO_BORDER)
        backBtn = wx.BitmapButton(self,
                                  size=(200, 80), name="button", bitmap=back)
        backBtn.SetBackgroundColour(wx.LIGHT_GREY)
        backBtn.SetWindowStyleFlag(wx.NO_BORDER)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(40)
        newBtn.Bind(wx.EVT_BUTTON, self.handle_new_calendar_parti)
        btnBox.Add(newBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.AddSpacer(60)
        sizer.Add(title_row, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(100)
        sizer.Add(partiBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(50)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)
        self.frame.SetStatusText("participants names must be seperated with ' ,'")

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_new_calendar_parti(self, event):
        participants = self.partiField.GetValue()
        if not participants :
            self.frame.SetStatusText("Must enter participants")
        else:
            print(participants)
            participants = participants.split(", ")
            self.frame.graphics_q.put(("new cal parti", (participants)))

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.frame.SetStatusText("Red is the joined color")
        self.parent.calendar.Show()


class invitationsPanel(wx.Panel):
    def __init__(self, parent, frame, name="test", participants=None, manager="1", date="&&&", start = "16:00", end="18:00"):
        wx.Panel.__init__(self, parent, pos=parent.GetPosition(), size=parent.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.events = []
        mainbox = wx.BoxSizer(wx.VERTICAL)
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.backBtn = wx.Button(self, wx.ID_ANY, label="back", size=(100, 40))
        self.backBtn.Bind(wx.EVT_BUTTON, self.go_back)
        btnBox.Add(self.backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(650)
        mainbox.Add(btnBox)
        mainbox.AddSpacer(10)

        if participants:
            # title
            title_row = wx.BoxSizer(wx.HORIZONTAL)
            title = wx.StaticText(self, -1, label=name)
            titlefont = wx.Font(45, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
            eventfont = wx.Font(25, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
            smallTitleFont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
            title.SetForegroundColour(wx.BLACK)
            title.SetFont(titlefont)
            #arrrow button
            left = wx.Image("pics\\left.png")
            left.Rescale(100, 80)
            right = wx.Image("pics\\right.png")
            right.Rescale(100, 80)
            left = wx.Bitmap(left)
            right = wx.Bitmap(right)
            # create button at point (20, 20)
            self.leftBtn = wx.BitmapButton(self,
                                size=(100, 80), pos=(100,50), name="button", bitmap=left)
            self.leftBtn.SetBackgroundColour(wx.LIGHT_GREY)
            self.leftBtn.SetWindowStyleFlag(wx.NO_BORDER)
            self.rightBtn = wx.BitmapButton(self,
                                           size=(100, 80), pos=(660, 50), name="button", bitmap=right)
            self.rightBtn.SetBackgroundColour(wx.LIGHT_GREY)
            self.rightBtn.SetWindowStyleFlag(wx.NO_BORDER)
            self.leftBtn.Bind(wx.EVT_BUTTON, self.left_invitation)
            self.rightBtn.Bind(wx.EVT_BUTTON, self.right_invitation)

            # set bmp as bitmap for button
            title_row.Add(self.leftBtn, 1, wx.ALL, 5)
            title_row.AddSpacer(200)
            title_row.Add(title, 1, wx.ALL, 5)
            title_row.AddSpacer(200)
            title_row.Add(self.rightBtn, 1, wx.ALL, 5)

            if date != "&&&":
                date_row = wx.BoxSizer(wx.HORIZONTAL)
                date = wx.StaticText(self, -1, label=date)
                date.SetForegroundColour(wx.BLACK)
                date.SetFont(eventfont)
                date_title = wx.StaticText(self, -1, label="Date:   ")
                date_title.SetForegroundColour(wx.BLACK)
                date_title.SetFont(smallTitleFont)
                date_row.Add(date_title)
                date_row.Add(date)

                time_str = start + " - " + end
                time_row = wx.BoxSizer(wx.HORIZONTAL)
                time = wx.StaticText(self, -1, label=time_str)
                time.SetForegroundColour(wx.BLACK)
                time.SetFont(eventfont)
                time_title = wx.StaticText(self, -1, label="Time:   ")
                time_title.SetForegroundColour(wx.BLACK)
                time_title.SetFont(smallTitleFont)
                time_row.Add(time_title)
                time_row.Add(time)

            participants_str = ", ".join(participants)
            participants_row = wx.BoxSizer(wx.HORIZONTAL)
            parti = wx.StaticText(self, -1, label=participants_str)
            parti.SetForegroundColour(wx.BLACK)
            parti.SetFont(eventfont)
            parti_title = wx.StaticText(self, -1, label="Participants:   ")
            parti_title.SetForegroundColour(wx.BLACK)
            parti_title.SetFont(smallTitleFont)
            participants_row.Add(parti_title)
            participants_row.Add(parti)

            manager_row = wx.BoxSizer(wx.HORIZONTAL)
            manager = wx.StaticText(self, -1, label=manager)
            manager.SetForegroundColour(wx.BLACK)
            manager.SetFont(eventfont)
            manager_title = wx.StaticText(self, -1, label="Invited by:   ")
            manager_title.SetForegroundColour(wx.BLACK)
            manager_title.SetFont(smallTitleFont)
            manager_row.Add(manager_title)
            manager_row.Add(manager)

            buttons = wx.BoxSizer(wx.HORIZONTAL)
            acceptBtn = wx.Button(self, wx.ID_ANY, label="accept", size=(100, 40))
            acceptBtn.Bind(wx.EVT_BUTTON, self.accept)
            buttons.Add(acceptBtn, 0, wx.ALL, 5)
            buttons.AddSpacer(30)
            declineBtn = wx.Button(self, wx.ID_ANY, label="decline", size=(100, 40))
            declineBtn.Bind(wx.EVT_BUTTON, self.decline)
            buttons.Add(declineBtn, 0, wx.ALL, 5)

            mainbox.AddSpacer(40)
            mainbox.Add(title_row, 0, wx.CENTER)
            mainbox.AddSpacer(40)
            if date != "&&&":
                mainbox.Add(date_row, 0, wx.CENTER)
                mainbox.AddSpacer(20)
                mainbox.Add(time_row, 0, wx.CENTER)
                mainbox.AddSpacer(20)
            mainbox.Add(participants_row, 0, wx.CENTER)
            mainbox.AddSpacer(20)
            mainbox.Add(manager_row, 0, wx.CENTER)
            mainbox.AddSpacer(50)
            mainbox.Add(buttons, 0, wx.CENTER)

        else:
            # title
            print("hereeeee")
            print(date)
            mainbox.AddSpacer(200)
            title = wx.StaticText(self, -1, label="There are no invitations")
            titlefont = wx.Font(45, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
            title.SetForegroundColour(wx.BLACK)
            title.SetFont(titlefont)
            mainbox.Add(title, 0, wx.CENTER)
            self.parent.uncolor_invitation()

        self.SetSizer(mainbox)
        self.Layout()
        self.Hide()


    def left_invitation(self, evt):
        print("scroll to left invitation")
        self.frame.graphics_q.put(("left invitation", ()))

    def right_invitation(self, evt):
        print("scroll to right invitation")
        self.frame.graphics_q.put(("right invitation", ()))

    def go_back(self, evt):
        self.Hide()
        self.frame.SetStatusText("Red is the joined color")
        self.parent.calendar.Show()

    def accept(self, evt):
        self.frame.graphics_q.put(("response", ("0")))

    def decline(self, evt):
        self.frame.graphics_q.put(("response", ("1")))


class newEventParticipantPanel(wx.Panel):
    def __init__(self, parent, frame, event_name="test"):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=frame.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        title_row = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, -1, label=event_name)
        title.SetForegroundColour(wx.BLACK)
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        titleStart = wx.StaticText(self, -1, label="Add participants to ")
        titleStart.SetForegroundColour(wx.BLACK)
        titleStart.SetFont(titlefont)
        title_row.Add(titleStart)
        title_row.Add(title)
        smallfont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        # participants
        partiBox = wx.BoxSizer(wx.HORIZONTAL)
        partiText = wx.StaticText(self, 1, label="Participants to add: ")
        partiText.SetFont(smallfont)
        self.partiField = wx.TextCtrl(self, -1, name="participants", size=(300, 50))
        self.partiField.SetFont(smallfont)
        partiBox.Add(partiText, 0, wx.ALL, 5)
        partiBox.Add(self.partiField, 0, wx.ALL, 5)

        newP = wx.Image("pics\\done.png")
        newP.Rescale(250, 100)
        back = wx.Image("pics\\back.png")
        back.Rescale(200, 80)
        back = wx.Bitmap(back)
        newP = wx.Bitmap(newP)
        newBtn = wx.BitmapButton(self,
                                 size=(200, 80), name="button", bitmap=newP)
        newBtn.SetBackgroundColour(wx.LIGHT_GREY)
        newBtn.SetWindowStyleFlag(wx.NO_BORDER)
        backBtn = wx.BitmapButton(self,
                                  size=(200, 80), name="button", bitmap=back)
        backBtn.SetBackgroundColour(wx.LIGHT_GREY)
        backBtn.SetWindowStyleFlag(wx.NO_BORDER)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(40)
        newBtn.Bind(wx.EVT_BUTTON, self.handle_new_event_parti)
        btnBox.Add(newBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.AddSpacer(60)
        sizer.Add(title_row, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(100)
        sizer.Add(partiBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(50)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)
        self.frame.SetStatusText("participants names must be seperated with ' ,'")

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_new_event_parti(self, event):
        participants = self.partiField.GetValue()
        if not participants :
            self.frame.SetStatusText("Must enter participants")
        else:
            print(participants)
            participants = participants.split(", ")
            self.frame.graphics_q.put(("new evt parti", (participants)))

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.event.Show()


class newEventPanel(wx.Panel):
    def __init__(self, parent, frame, date="test date"):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=frame.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.date = date
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        titleBox = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, -1, label="New event on ")
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        title_date = wx.StaticText(self, -1, label=date)
        title_date.SetForegroundColour(wx.BLACK)
        title_date.SetFont(titlefont)
        titleBox.Add(title)
        titleBox.Add(title_date)

        smallfont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        # name
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        nameText = wx.StaticText(self, 1, label="Name of event: ")
        nameText.SetFont(smallfont)
        self.nameField = wx.TextCtrl(self, -1, name="name", size=(300, 50))
        self.nameField.SetFont(smallfont)
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)
        # participants
        partiBox = wx.BoxSizer(wx.HORIZONTAL)
        partiText = wx.StaticText(self, 1, label="Participants to add: ")
        partiText.SetFont(smallfont)
        self.partiField = wx.TextCtrl(self, -1, name="participants", size=(300, 50))
        self.partiField.SetFont(smallfont)
        partiBox.Add(partiText, 0, wx.ALL, 5)
        partiBox.Add(self.partiField, 0, wx.ALL, 5)
        # start hour
        startBox = wx.BoxSizer(wx.HORIZONTAL)
        startText = wx.StaticText(self, 1, label="Start hour: ")
        startText.SetFont(smallfont)
        self.startField = wx.TextCtrl(self, -1, name="start", size=(300, 50))
        self.startField.SetFont(smallfont)
        startBox.Add(startText, 0, wx.ALL, 5)
        startBox.Add(self.startField, 0, wx.ALL, 5)
        # end hour
        endBox = wx.BoxSizer(wx.HORIZONTAL)
        endText = wx.StaticText(self, 1, label="End hour: ")
        endText.SetFont(smallfont)
        self.endField = wx.TextCtrl(self, -1, name="end", size=(300, 50))
        self.endField.SetFont(smallfont)
        endBox.Add(endText, 0, wx.ALL, 5)
        endBox.Add(self.endField, 0, wx.ALL, 5)

        newE = wx.Image("pics\\done.png")
        newE.Rescale(250, 100)
        back = wx.Image("pics\\back.png")
        back.Rescale(200, 80)
        back = wx.Bitmap(back)
        newE = wx.Bitmap(newE)
        newBtn = wx.BitmapButton(self,
                                 size=(200, 80), name="button", bitmap=newE)
        newBtn.SetBackgroundColour(wx.LIGHT_GREY)
        newBtn.SetWindowStyleFlag(wx.NO_BORDER)
        backBtn = wx.BitmapButton(self,
                                  size=(200, 80), name="button", bitmap=back)
        backBtn.SetBackgroundColour(wx.LIGHT_GREY)
        backBtn.SetWindowStyleFlag(wx.NO_BORDER)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(40)
        newBtn.Bind(wx.EVT_BUTTON, self.handle_new_event)
        btnBox.Add(newBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.AddSpacer(40)
        sizer.Add(titleBox, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(50)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(10)
        sizer.Add(partiBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(10)
        sizer.Add(startBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(10)
        sizer.Add(endBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(30)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)
        self.frame.SetStatusText("participants names must be separated with ', '")

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_new_event(self, event):
        name = self.nameField.GetValue()
        participants = self.partiField.GetValue()
        start = self.startField.GetValue()
        end = self.endField.GetValue()
        if not name or not start or not end:
            self.frame.SetStatusText("Must enter name, start and end")
        else:
            if not participants:
                participants = ""
            participants = participants.split(", ")
            self.frame.graphics_q.put(("new event", (name, participants, start, end, self.date)))

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.event.Show()


class calNamePanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=frame.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        titleBox = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, -1, label="Change calendar name ")
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        titleBox.Add(title)

        smallfont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        # name
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        nameText = wx.StaticText(self, 1, label="New name: ")
        nameText.SetFont(smallfont)
        self.nameField = wx.TextCtrl(self, -1, name="name", size=(300, 50))
        self.nameField.SetFont(smallfont)
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)

        newN = wx.Image("pics\\done.png")
        newN.Rescale(250, 100)
        back = wx.Image("pics\\back.png")
        back.Rescale(200, 80)
        back = wx.Bitmap(back)
        newN = wx.Bitmap(newN)
        newBtn = wx.BitmapButton(self,
                                 size=(200, 80), name="button", bitmap=newN)
        newBtn.SetBackgroundColour(wx.LIGHT_GREY)
        newBtn.SetWindowStyleFlag(wx.NO_BORDER)
        backBtn = wx.BitmapButton(self,
                                  size=(200, 80), name="button", bitmap=back)
        backBtn.SetBackgroundColour(wx.LIGHT_GREY)
        backBtn.SetWindowStyleFlag(wx.NO_BORDER)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(40)
        newBtn.Bind(wx.EVT_BUTTON, self.handle_new_name)
        btnBox.Add(newBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.AddSpacer(60)
        sizer.Add(titleBox, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(60)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(40)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_new_name(self, event):
        name = self.nameField.GetValue()

        if not name:
            self.frame.SetStatusText("Must enter name")
        else:
            self.frame.graphics_q.put(("cal name", (name)))

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.calendar.Show()


class evtNamePanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=frame.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        titleBox = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, -1, label="Change event name ")
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        titleBox.Add(title)

        smallfont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        # name
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        nameText = wx.StaticText(self, 1, label="New name: ")
        nameText.SetFont(smallfont)
        self.nameField = wx.TextCtrl(self, -1, name="name", size=(300, 50))
        self.nameField.SetFont(smallfont)
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)

        newN = wx.Image("pics\\done.png")
        newN.Rescale(250, 100)
        back = wx.Image("pics\\back.png")
        back.Rescale(200, 80)
        back = wx.Bitmap(back)
        newN = wx.Bitmap(newN)
        newBtn = wx.BitmapButton(self,
                                 size=(200, 80), name="button", bitmap=newN)
        newBtn.SetBackgroundColour(wx.LIGHT_GREY)
        newBtn.SetWindowStyleFlag(wx.NO_BORDER)
        backBtn = wx.BitmapButton(self,
                                  size=(200, 80), name="button", bitmap=back)
        backBtn.SetBackgroundColour(wx.LIGHT_GREY)
        backBtn.SetWindowStyleFlag(wx.NO_BORDER)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(40)
        newBtn.Bind(wx.EVT_BUTTON, self.handle_new_name)
        btnBox.Add(newBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.AddSpacer(60)
        sizer.Add(titleBox, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(60)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(40)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_new_name(self, event):
        name = self.nameField.GetValue()

        if not name:
            self.frame.SetStatusText("Must enter name")
        else:
            self.frame.graphics_q.put(("evt name", (name)))

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.event.Show()


class evtTimePanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=frame.GetSize())
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        titleBox = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, -1, label="Change event time ")
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        titleBox.Add(title)

        smallfont = wx.Font(20, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)

        # date
        dateBox = wx.BoxSizer(wx.HORIZONTAL)
        dateText = wx.StaticText(self, 1, label="New date: ")
        dateText.SetFont(smallfont)
        self.dateField = wx.TextCtrl(self, -1, name="date", size=(300, 50))
        self.dateField.SetFont(smallfont)
        dateBox.Add(dateText, 0, wx.ALL, 5)
        dateBox.Add(self.dateField, 0, wx.ALL, 5)

        # start
        startBox = wx.BoxSizer(wx.HORIZONTAL)
        startText = wx.StaticText(self, 1, label="New start hour: ")
        startText.SetFont(smallfont)
        self.startField = wx.TextCtrl(self, -1, name="date", size=(300, 50))
        self.startField.SetFont(smallfont)
        startBox.Add(startText, 0, wx.ALL, 5)
        startBox.Add(self.startField, 0, wx.ALL, 5)

        # end
        endBox = wx.BoxSizer(wx.HORIZONTAL)
        endText = wx.StaticText(self, 1, label="New end hour: ")
        endText.SetFont(smallfont)
        self.endField = wx.TextCtrl(self, -1, name="date", size=(300, 50))
        self.endField.SetFont(smallfont)
        endBox.Add(endText, 0, wx.ALL, 5)
        endBox.Add(self.endField, 0, wx.ALL, 5)

        newT = wx.Image("pics\\done.png")
        newT.Rescale(250, 100)
        back = wx.Image("pics\\back.png")
        back.Rescale(200, 80)
        back = wx.Bitmap(back)
        newT = wx.Bitmap(newT)
        newBtn = wx.BitmapButton(self,
                                 size=(200, 80), name="button", bitmap=newT)
        newBtn.SetBackgroundColour(wx.LIGHT_GREY)
        newBtn.SetWindowStyleFlag(wx.NO_BORDER)
        backBtn = wx.BitmapButton(self,
                                  size=(200, 80), name="button", bitmap=back)
        backBtn.SetBackgroundColour(wx.LIGHT_GREY)
        backBtn.SetWindowStyleFlag(wx.NO_BORDER)

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(40)
        newBtn.Bind(wx.EVT_BUTTON, self.handle_new_time)
        btnBox.Add(newBtn, 0, wx.ALL, 5)

        # add all elements to sizer
        sizer.AddSpacer(40)
        sizer.Add(titleBox, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(40)
        sizer.Add(dateBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(20)
        sizer.Add(startBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(20)
        sizer.Add(endBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(40)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        # arrange the screen
        self.SetSizer(sizer)
        self.Layout()
        self.Hide()

    def handle_new_time(self, event):
        date = self.dateField.GetValue()
        start = self.startField.GetValue()
        end = self.endField.GetValue()


        if not date or not start or not end:
            self.frame.SetStatusText("Must enter date, start hour and end hour")
        else:
            self.frame.graphics_q.put(("evt time", (date, start, end)))

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.event.Show()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()