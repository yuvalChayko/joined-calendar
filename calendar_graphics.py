import wx
import wx.adv
from wx.adv import CalendarCtrl, GenericCalendarCtrl, CalendarDateAttr

class MyFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MyFrame, self).__init__(parent, title="Example for Calanders", size=(500,500))
        # create status bar
        self.CreateStatusBar(1)
        self.SetStatusText("Developed by Merry Geva 1/1/2000")
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
        #self.login = LoginPanel(self, self.frame)
        #self.registration = RegistrationPanel(self, self.frame)
        #self.files = FilesPanel(self,self.frame)

        self.cal = CalandarPanel(self, self.frame)

        # v_box.Add(self.login)
        # v_box.Add(self.registration)
        # v_box.Add(self.files)
        v_box.Add(self.cal)
        # The first panel to show
        self.cal.Show()
        self.SetSizer(v_box)
        self.Layout()


class CalandarPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent, )
        self.frame = frame

        title = wx.StaticText(self,-1, label="Merry's Calendars")
        titlefont = wx.Font(22, wx.DECORATIVE, wx.NORMAL, wx.NORMAL)
        title.SetForegroundColour(wx.BLACK)
        title.SetFont(titlefont)


        mainbox = wx.BoxSizer(wx.VERTICAL)
        mainbox.Add(title, 1, wx.CENTER)


        native = self.cal = CalendarCtrl(self, -1, wx.DateTime().Today(),
                                    style=wx.adv.CAL_SEQUENTIAL_MONTH_SELECTION, name="cal-1")



        cal = GenericCalendarCtrl(self, -1, wx.DateTime().Today(),
                                  style = wx.adv.CAL_SHOW_HOLIDAYS
                                        | wx.adv.CAL_SUNDAY_FIRST
                                        | wx.adv.CAL_SEQUENTIAL_MONTH_SELECTION,name="cal-2")
        #cal.SetHolidayColours(colBg="green", colFg="red")



        cal2 = GenericCalendarCtrl(self, -1, wx.DateTime().Today(), name="cal-3")


        # Track a few holidays
        self.holidays = [(1,1), (10,31), (12,25) ]    # (these don't move around)
        self.OnChangeMonth()


        # bind some event handlers to each calendar
        for c in [native, cal, cal2]:
            c.Bind(wx.adv.EVT_CALENDAR,                 self.OnCalSelected)
            c.Bind(wx.adv.EVT_CALENDAR_MONTH,           self.OnChangeMonth)
            c.Bind(wx.adv.EVT_CALENDAR_SEL_CHANGED,     self.OnCalSelChanged)
            c.Bind(wx.adv.EVT_CALENDAR_WEEKDAY_CLICKED, self.OnCalWeekdayClicked)



        # create some sizers for layout
        fgs = wx.FlexGridSizer(cols=2, hgap=50, vgap=50)
        # calendar - 1
        v_box = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(self, -1, "Calendar-1")
        v_box.Add(txt)
        v_box.Add(native)
        fgs.Add(v_box)


        # calendar - 2
        v_box = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(self, -1, "Calendar-2")
        v_box.Add(txt)
        v_box.Add(cal)
        fgs.Add(v_box)

        # calendar - 3
        v_box = wx.BoxSizer(wx.VERTICAL)
        txt = wx.StaticText(self, -1, "Calendar-3")
        v_box.Add(txt)
        v_box.Add(cal2)
        fgs.Add(v_box)

        box = wx.BoxSizer()
        box.Add(fgs, 1, wx.EXPAND|wx.ALL, 25)

        mainbox.Add(box, 1, wx.EXPAND)
        self.SetSizer(mainbox)


    def OnCalSelected(self, evt):
        print('OnCalSelected: %s\n' % evt.Date)
        if evt.Date.month == wx.DateTime.Aug and evt.Date.day == 14:
            print("HAPPY BIRTHDAY!")

        cal = evt.GetEventObject()
        print('name: %s\n' % cal.GetName())

    def OnCalWeekdayClicked(self, evt):
        print('OnCalWeekdayClicked: %s\n' % evt.GetWeekDay())

        cal = evt.GetEventObject()
        print('name: %s\n' % cal.GetName())

    def OnCalSelChanged(self, evt):
        cal = evt.GetEventObject()
        print("OnCalSelChanged:\n\t%s: %s\n\t%s: %s" %
                       ("EventObject", cal.__class__,
                        "Date       ", cal.GetDate(),
                        ))
        print('name: %s\n' % cal.GetName())

    def OnChangeMonth(self, evt=None):
        if evt is None:
            cal = self.cal
        else:
            cal = evt.GetEventObject()
        print('OnChangeMonth: %s\n' % cal.GetDate())
        cur_month = cal.GetDate().GetMonth() + 1   # convert wxDateTime 0-11 => 1-12
        for month, day in self.holidays:
            if month == cur_month:
                print("holiday....", day, month)
                cal.SetHoliday(day)



        # August 14th is a special day, mark it with a blue square...
        if cur_month == 8:
            attr = CalendarDateAttr(border=wx.adv.CAL_BORDER_SQUARE,
                                          colBorder="blue")
            cal.SetAttr(14, attr)
        else:
            cal.ResetAttr(14)

        print('name: %s\n' % cal.GetName())



if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()