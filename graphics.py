import wx

class MyFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MyFrame, self).__init__(parent, title="joined calendar", size=(500, 500))
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
        self.frame = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        v_box = wx.BoxSizer()
        # create object for each panel
        self.login = LoginPanel(self, self.frame)
        self.first = FirstPanel(self, self.frame)
        self.registration = RegistrationPanel(self, self.frame)
        # v_box.Add(self.login)
        # v_box.Add(self.registration)
        # The first panel to show
        self.SetSizer(v_box)
        self.Layout()
        self.first.Show()


class LoginPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        title = wx.StaticText(self,-1, label="Login")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        # username
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        nameText = wx.StaticText(self, 1, label="Username: ")
        self.nameField = wx.TextCtrl(self, -1, name="username", size=(150, -1))
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)
        # password
        passBox = wx.BoxSizer(wx.HORIZONTAL)
        passText = wx.StaticText(self, 1, label="Password: ")
        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size=(150, -1))
        passBox.Add(passText, 0, wx.ALL, 5)
        passBox.Add(self.passField, 0,  wx.ALL, 5)
        # login & registration buttons
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        backBtn = wx.Button(self, wx.ID_ANY, label="Back", size=(100, 40))
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        loginBtn = wx.Button(self, wx.ID_ANY, label="login", size=(100, 40))
        loginBtn.Bind(wx.EVT_BUTTON, self.handle_login)
        btnBox.Add(loginBtn, 0, wx.ALL, 5)
        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(10)
        sizer.Add(nameBox,0, wx.CENTER | wx.ALL, 5)
        sizer.Add(passBox,-1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(10)
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
            self.frame.SetStatusText("waiting for Server approve")

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.first.Show()

class RegistrationPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        title = wx.StaticText(self,-1, label="Register")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        # username
        nameBox = wx.BoxSizer(wx.HORIZONTAL)
        nameText = wx.StaticText(self, 1, label="Username: ")
        self.nameField = wx.TextCtrl(self, -1, name="username", size=(150, -1))
        nameBox.Add(nameText, 0, wx.ALL, 5)
        nameBox.Add(self.nameField, 0, wx.ALL, 5)
        # password
        passBox = wx.BoxSizer(wx.HORIZONTAL)
        passText = wx.StaticText(self, 1, label="Password: ")
        self.passField = wx.TextCtrl(self, -1, name="password", style=wx.TE_PASSWORD, size=(150, -1))
        passBox.Add(passText, 0, wx.ALL, 5)
        passBox.Add(self.passField, 0,  wx.ALL, 5)
        # phone number
        phoneBox = wx.BoxSizer(wx.HORIZONTAL)
        phoneText = wx.StaticText(self, 1, label="Phone:      ")
        self.phoneField = wx.TextCtrl(self, -1, name="Phone", size=(150, -1))
        phoneBox.Add(phoneText, 0, wx.ALL, 5)
        phoneBox.Add(self.phoneField, 0,  wx.ALL, 5)
        # login & registration buttons
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        backBtn = wx.Button(self, wx.ID_ANY, label="Back", size=(100, 40))
        backBtn.Bind(wx.EVT_BUTTON, self.handle_back)
        btnBox.Add(backBtn, 1, wx.ALL, 5)
        registerBtn = wx.Button(self, wx.ID_ANY, label="register", size=(100, 40))
        registerBtn.Bind(wx.EVT_BUTTON, self.handle_registration)
        btnBox.Add(registerBtn, 0, wx.ALL, 5)
        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(10)
        sizer.Add(nameBox, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(passBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.Add(phoneBox, -1, wx.CENTER | wx.ALL, 5)
        sizer.AddSpacer(10)
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
            self.frame.SetStatusText("waiting for Server approve")

    def handle_back(self, event):
        self.frame.SetStatusText("")
        self.Hide()
        self.parent.first.Show()


class FirstPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, pos=wx.DefaultPosition, size=(500, 500))
        self.frame = frame
        self.parent = parent
        self.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        # title
        title = wx.StaticText(self, -1, label="joined calendar")
        titlefont = wx.Font(30, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)
        # login & registration buttons
        btnBox = wx.BoxSizer(wx.HORIZONTAL)
        loginBtn = wx.Button(self, wx.ID_ANY, label="login", size=(150, 200))
        loginBtn.Bind(wx.EVT_BUTTON, self.handle_login)
        btnBox.Add(loginBtn, 0, wx.ALL, 5)
        # add all elements to sizer
        sizer.Add(title, 0, wx.CENTER | wx.TOP, 5)
        sizer.AddSpacer(30)
        sizer.Add(btnBox, wx.CENTER | wx.ALL, 5)

        backBtn = wx.Button(self, wx.ID_ANY, label="registeration", size=(150, 200))
        backBtn.Bind(wx.EVT_BUTTON, self.handle_reg)
        btnBox.Add(backBtn, 1, wx.ALL, 5)

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


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame()
    frame.Show()
    app.MainLoop()