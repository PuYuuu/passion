import wx

import application

class Manager():

    def __init__(self,UpdateUI):
        self.UpdateUI = UpdateUI
        self.frameDict = {} # 用来装载已经创建的Frame对象

    def GetFrame(self,number):
        frame = self.frameDict.get(number)

        if frame:
            pass
        else:
            frame = self.CreateFrame(number)
            self.frameDict[number] = frame

        return frame

    def CreateFrame(self,number):
        if number == 1:
            return application.UIFrame(UpdateUI=self.UpdateUI)
        elif number == 2:
            return application.SUBFrame(UpdateUI=self.UpdateUI)