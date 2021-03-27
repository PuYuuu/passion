# -*- coding: utf-8 -*- 
import wx
import application
from guimanager import Manager

class MainApp(wx.App):

    def OnInit(self):
        self.guimanager = Manager(self.UpdateUI)
        self.frame = self.guimanager.GetFrame(number = 1)
        self.frame.Show()
        return True

    def UpdateUI(self,number):
        self.frame = self.guimanager.GetFrame(number)
        self.frame.Show(True)
    
if __name__ == '__main__':
    app = MainApp()
    app.MainLoop()