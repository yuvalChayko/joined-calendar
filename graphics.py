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
        pub.subscribe(self.mark_dates, "mark")
        pub.subscribe(self.unmark_dates, "unmark")
        pub.subscribe(self.hide_panel, "hide")
        self.frame = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        self.v_box = wx.BoxSizer(wx.VERTICAL)
        # create object for each panel
        self.login = LoginPanel(self, self.frame)
        self.first = FirstPanel(self, self.frame)
        self.registration = RegistrationPanel(self, self.frame)
        self.calendar = CalendarPanel(self, self.frame)
        self.v_box.Add(self.login,1, wx.EXPAND)
        self.v_box.Add(self.registration, 1,wx.EXPAND)
        self.v_box.Add(self.calendar, 1,wx.EXPAND)
        self.v_box.Add(self.first, 1,wx.EXPAND)


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
        self.calendar.Show()



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
            self.calendar.Hide()


    def mark_dates(self, dates):
        """
        mark dates with events
        :param dates:
        :return:
        """
        self.calendar.mark_dates(dates)


    def unmark_dates(self, dates):
        """
        unmark dates with events
        :param dates:
        :return:
        """
        self.calendar.unmark_dates(dates)


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

        title_row = wx.BoxSizer(wx.HORIZONTAL)
        # title
        title = wx.StaticText(self, -1, label=name)
        titlefont = wx.Font(40, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        calfont = wx.Font(35, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
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
        self.leftBtn.Bind(wx.EVT_BUTTON, self.left_cal)
        self.rightBtn.Bind(wx.EVT_BUTTON, self.right_cal)

        # set bmp as bitmap for button
        #self.leftBtn.SetBitmap(left)
        #self.rightBtn.SetBitmap(right)
        title_row.Add(self.leftBtn, 1, wx.ALL, 5)
        title_row.Add(self.rightBtn, 1, wx.ALL, 5)
        btnBox2 = wx.BoxSizer(wx.HORIZONTAL)
        changeBtn = wx.Button(self, wx.ID_ANY, label="change name", size=(100, 40), pos=(765,95))
        changeBtn.Bind(wx.EVT_BUTTON, self.change_calendar_name)
        btnBox2.Add(changeBtn, 0, wx.ALL, 5)
        addBtn = wx.Button(self, wx.ID_ANY, label="add participant", size=(100, 40), pos=(765,50))
        addBtn.Bind(wx.EVT_BUTTON, self.add_calendar_participant)
        btnBox2.Add(addBtn, 0, wx.ALL, 5)



        title_row.Add(title, 1, wx.ALL, 5)
        title_row.Add(btnBox2, 0, wx.ALL, 5)




        # participants = ["1", "2", "3"]
        # p_text = wx.StaticText(self, -1, "participants: ", pos = (430, 30))
        # p = wx.Choice(self, -1, pos = (450, 30), choices=participants)

        mainbox = wx.BoxSizer(wx.VERTICAL)

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

        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        self.partBtn = wx.Button(self, wx.ID_ANY, label="participants", size=(100, 40))
        self.partBtn.Bind(wx.EVT_BUTTON, self.display)
        btnBox.Add(self.partBtn, 1, wx.ALL, 5)
        btnBox.AddSpacer(650)
        newBtn = wx.Button(self, wx.ID_ANY, label="new calendar", size=(100, 40))
        newBtn.Bind(wx.EVT_BUTTON, self.new_calendar)
        btnBox.Add(newBtn, 0, wx.ALL, 5)
        self.myScrolled = ParticipantsPanel(self, self.frame,self.partBtn, participants)


        mainbox.Add(btnBox)

        mainbox.AddSpacer(20)
        # mainbox.Add(self.partBtn,  0, wx.ALL, 5)


        mainbox.Add(title, 0, wx.CENTER)


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
        mainbox.AddSpacer(20)
        mainbox.Add(self.cal,0, wx.ALL | wx.CENTER,5)



        #box = wx.BoxSizer()
        #box.Add(fgs, 1, wx.EXPAND | wx.ALL, 25)

        #mainbox.Add(calSizer, 1, wx.EXPAND)


        self.SetSizer(mainbox)
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
        print(month_num)
        print(self.current_month)
        if month_num != self.current_month:
            self.current_month = month_num
            year = str(cal.GetDate())[-4:]
            self.frame.graphics_q.put(("month", (month_num, year)))



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

    def left_cal(self, evt):
        print("scroll to left cal")
        self.frame.graphics_q.put(("left", ()))

    def right_cal(self, evt):
        print("scroll to right cal")
        self.frame.graphics_q.put(("right", ()))


    def change_calendar_name(self, evt):
        print("try to change calendar name")

    def add_calendar_participant(self, evt):
        print("try to add participant to calendar")

    def mark_dates(self, dates):
        for i in dates:
            self.cal.SetAttr(i[0], wx.adv.CalendarDateAttr(colBack=i[1]))

    def unmark_dates(self, dates):
        for i in dates:
            self.cal.ResetAttr(i)




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
        for parti in self.participants:
            user = wx.TextCtrl(self.scrollP, value=parti)
            self.spSizer.Add(user)
        self.scrollP.SetSizer(self.spSizer)

        if self.closeBtn:
            self.closeBtn.Destroy()


        self.closeBtn = wx.Button(self, wx.ID_ANY, label="close", size=(100, 20))
        self.closeBtn.Bind(wx.EVT_BUTTON, self.close)
        self.main_box.Add(self.closeBtn, 0, wx.ALL, 5)


        self.SetSizer(self.main_box)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()