import wx
import threading
import time

import var as v
import api

class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Coconuts " + v.VER, pos=(300,200),
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

        # self.resultText = wx.TextCtrl(panel, -1, '', size=(250,100), style=
        #                               wx.TE_MULTILINE
        #                             | wx.TE_READONLY
        #                               )
        # self.resultText.SetValue('')

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(self.OkBtn, 0, wx.LEFT, 20)
        btnSizer.Add(self.cancelBtn, 0, wx.LEFT, 40)

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

        pppoeBox = wx.StaticBox(panel, -1, 'PPPoE', size=(250,-1))
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
                          wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, 5)

        pppoeSizer.Add(pppoeColSizer, 0, wx.LEFT, 5)
        pppoeSizer.Add(pppoeCol2Sizer, 0, wx.LEFT, 2)

        wifiBox = wx.StaticBox(panel, -1, 'WiFi', size=(250,-1))
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
                          wx.ALIGN_RIGHT | wx.TOP | wx.LEFT, 5)

        wifiSizer.Add(wifiColSizer, 0, wx.LEFT, 5)
        wifiSizer.Add(wifiCol2Sizer, 0, wx.LEFT, 2)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(pppoeSizer, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 10)
        mainSizer.Add(wifiSizer, 0, wx.EXPAND | wx.ALL, 10)
        # mainSizer.Add(self.resultText, 0, wx.ALL, 10)
        mainSizer.Add(btnSizer, 0, wx.TOP | wx.BOTTOM, 20)

        panel.SetSizer(mainSizer)
        mainSizer.Fit(self)
        mainSizer.SetSizeHints(self)


    def connectionThread(self, ip, password, init=0):
        webClient = api.HttpClient()
        ret = webClient.connect(init=init, host=ip, password=password)
        if not ret:
            dlg = wx.MessageDialog(self, 'Connection is failed. please check your network!',
                                    'Info',
                                    wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP
                                    # wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                    )
            dlg.ShowModal()
            dlg.Destroy()
            return
        else:
            keepGoing = True
            self.dlg2 = wx.ProgressDialog('Init Router',
                                          "Running...\n",
                                         maximum=10,
                                         parent=self,
                                         style=0
                                               | wx.PD_APP_MODAL
                                               | wx.PD_CAN_ABORT
                                               ##                                | wx.PD_CAN_SKIP
                                               | wx.PD_ELAPSED_TIME
                                               # | wx.PD_REMAINING_TIME
                                               # | wx.PD_AUTO_HIDE
                                         )

            initProcess = self.InitPPPOEWifi(webClient, v.PPPOE_ACCOUNT, v.PPPOE_PASSWORD,
                                             v.WIFI_SSID, v.WIFI_PASSWORD)
            initProcess.start()
            # while keepGoing and memMon.curr_count <= v.COUNT:
            while keepGoing and initProcess.isAlive():
                time.sleep(1)
                wx.Yield()  # refresh progress
                (keepGoing, skip) = self.dlg2.Pulse(initProcess.resultText)


            self.running = False
            self.dlg2.Destroy()
            self.OkBtn.Enable(True)

    class InitPPPOEWifi(threading.Thread):
        def __init__(self, terminal, account, password, ssid, wifipassword):
            threading.Thread.__init__(self)
            self.terminal = terminal
            self.account = account
            self.password = password
            self.ssid = ssid
            self.wifiPassword = wifipassword
            self.resultText = "Running...\n"
            self.running = False

        def run(self):
            self.running = True
            if self.running is True:
                option = {
                    'wanType': 'pppoe',
                    'pppoeName': self.account,
                    'pppoePwd': self.password,
                }
                ret = api.setWan(self.terminal, **option)
                if ret is False:
                    self.resultText += "Config pppoe..........failed\n"
                else:
                    count = 0
                    self.resultText += "Config pppoe..."
                    ret2 = api.getPPPOEStatus(self.terminal)
                    while ret2.get("status") == 1 and count < 10:
                        time.sleep(2)
                        self.resultText += "."
                        count += 1
                        ret2 = api.getPPPOEStatus(self.terminal)
                    if ret2.get("status") == 2:
                        self.resultText += "done\n"
                    else:
                        self.resultText += "failed\n"

            if self.running is True:
                option2 = {
                    'name': 'coconuts',
                    'locale': 'company',
                    'ssid': v.WIFI_SSID,
                    'encryption': 'mixed-psk',
                    'password': v.WIFI_PASSWORD,
                    'txpwr': 1,
                }

                ret3 = api.setRouterNormal(self.terminal, **option2)
                if ret3 is False:
                    self.resultText += "Initialize xiaoqiang..........failed"
                else:
                    self.resultText += "Initialize xiaoqiang..."
                    count = 0
                    ret4 = api.getWifiStatus(self.terminal)
                    while int(ret4['status'][0]['up']) != 1 and count < 10:
                        time.sleep(2)
                        self.resultText += "."
                        count += 1
                        ret4 = api.getWifiStatus(self.terminal)
                    if int(ret4['status'][0]['up']) == 1:
                        self.resultText += "done\n"
                    else:
                        self.resultText += "failed\n"
            time.sleep(20)

        def stop(self):
            self.running = False


    def EvtOnClickClose(self, event):
        frame.Close(True)

    def EvtOnClickOk(self, event):
        self.OkBtn.Enable(False)
        v.PPPOE_ACCOUNT = self.account.GetValue()
        v.PPPOE_PASSWORD = self.password.GetValue()
        v.WIFI_SSID = self.wifiSsid.GetValue()
        v.WIFI_PASSWORD = self.wifiPassword.GetValue()
        dutConn = threading.Thread(target=self.connectionThread,
                                   kwargs={'ip': v.HOST, 'password': v.WEB_PWD, 'init': 1})
        dutConn.start()

    def EvtOnClickCloseWindow(self, event):
        self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = Frame()
    frame.Show()
    app.MainLoop()
