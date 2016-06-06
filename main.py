import wx

import var as v

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Coconuts", pos=(300,200),
                          style=
                          wx.CAPTION
                          | wx.CLOSE_BOX
                          | wx.MINIMIZE_BOX
                          | wx.SYSTEM_MENU
        )
        panel = wx.Panel(self)

        self.OkBtn = wx.Button(panel, -1, 'Ok')
        self.Bind(wx.EVT_BUTTON, self.EvtOnClickOk, self.OkBtn)

        self.cancelBtn = wx.Button(panel, -1, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.EvtOnClickClose, self.cancelBtn)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(self.OkBtn, 0, wx.LEFT, 20)
        btnSizer.Add(self.cancelBtn, 0, wx.LEFT | wx.RIGHT, 20)

        self.accLbl = wx.StaticText(panel, -1, 'Account:')
        self.account = wx.TextCtrl(panel, -1, '')
        self.account.SetValue(v.PPPOE_ACCOUNT)

        self.passwordLbl = wx.StaticText(panel, -1, 'Password:')
        self.password = wx.TextCtrl(panel, -1, '')
        self.password.SetValue(v.PPPOE_PASSWORD)

        self.wifiSsidLbl = wx.StaticText(panel, -1, 'SSID:')
        self.wifiSsid = wx.TextCtrl(panel, -1, '')
        self.wifiSsid.SetValue(v.WIFI_SSID)

        self.wifiPasswordLbl = wx.StaticText(panel, -1, 'Password:')
        self.wifiPassword = wx.TextCtrl(panel, -1, '')
        self.wifiPassword.SetValue(v.WIFI_PASSWORD)

        pppoeBox = wx.StaticBox(panel, -1, 'PPPOE')
        pppoeSizer = wx.StaticBoxSizer(pppoeBox, wx.HORIZONTAL)

        pppoeColSizer = wx.BoxSizer(wx.VERTICAL)
        pppoeColSizer.Add(self.accLbl, 0,
                          wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, 10)
        pppoeColSizer.Add(self.passwordLbl, 0,
                          wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, 10)

        pppoeCol2Sizer = wx.BoxSizer(wx.VERTICAL)
        pppoeCol2Sizer.Add(self.account, 0,
                          wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, 10)
        pppoeCol2Sizer.Add(self.password, 0,
                          wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, 10)

        pppoeSizer.Add(pppoeColSizer, 0, wx.LEFT, 5)
        pppoeSizer.Add(pppoeCol2Sizer, 0, wx.LEFT, 2)

        wifiBox = wx.StaticBox(panel, -1, 'WiFi')
        wifiSizer = wx.StaticBoxSizer(wifiBox, wx.HORIZONTAL)

        wifiColSizer = wx.BoxSizer(wx.VERTICAL)
        wifiColSizer.Add(self.wifiSsidLbl, 0,
                         wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, 10)
        wifiColSizer.Add(self.wifiPasswordLbl, 0,
                         wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, 10)

        wifiCol2Sizer = wx.BoxSizer(wx.VERTICAL)
        wifiCol2Sizer.Add(self.wifiSsid, 0,
                          wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, 10)
        wifiCol2Sizer.Add(self.wifiPassword, 0,
                          wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, 10)

        wifiSizer.Add(wifiColSizer, 0, wx.LEFT, 5)
        wifiSizer.Add(wifiCol2Sizer, 0, wx.LEFT, 2)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add((1,100))
        mainSizer.Add(pppoeSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        mainSizer.Add(wifiSizer, 0, wx.EXPAND | wx.ALL, 10)
        mainSizer.Add(btnSizer, 0, wx.TOP | wx.BOTTOM, 20)

        panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)

    def EvtOnClickClose(self, event):
        frame.Close(True)

    def EvtOnClickOk(self, event):
        v.PPPOE_ACCOUNT = self.account.GetValue()
        v.PPPOE_PASSWORD = self.password.GetValue()
        v.WIFI_SSID = self.wifiSsid.GetValue()
        v.WIFI_PASSWORD = self.wifiPassword.GetValue()


    def EvtOnClickCloseWindow(self, event):
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = Frame()
    frame.Show()
    app.MainLoop()
