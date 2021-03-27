# -*- coding: utf-8 -*- 
# @Descripttion : 该文件为上位机核心文件，在MyFrame.py文件GUI布局设计和xbee.py
#                 文件通信数据打包与解析的基础上完成了业务逻辑与功能代码
# @version      : V1.30
# @Author       : puyu
# @Date         : 2021-02-25 21:19:50
# LastEditors   : puyu
# LastEditTime  : 2021-03-18 21:32:52

import wx
import MyFrame
import xbee

import time
import numpy
import threading
import serial
from serial.tools import list_ports
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure


# 4个 Agent的坐标
pos_x = [0.0, 8.0, 16.0, 24.0]
pos_y = [0.0, 0.0, 0.0, 0.0]

# 3个follower的误差信息
errPos = [[],[],[]]     # 误差
errSam = []             # 时间步


# threading timer唤醒周期 
# 每 20ms处理一次串口缓存，每 40ms更新一次绘图
s_recvInterval = 0.020
s_plotInterval = 0.040

# 串口相关变量
# 固定 8位数据位 1位停止位 无奇偶校验位
s_serialPort = serial.Serial()
s_serialPort.bytesizes = serial.EIGHTBITS
s_serialPort.stopbits = serial.STOPBITS_ONE
s_serialPort.parity = serial.PARITY_NONE


class UIFrame(MyFrame.MyFrame1):
    def __init__(self, parent = None, UpdateUI = None):
        MyFrame.MyFrame1.__init__(self, parent)
        self.icon = wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.UpdateUI = UpdateUI
        self.isShowLocus = 0
        self.timerRev_running = 0
        self.timerPlo_running = 0
        self.timerPlo = threading.Timer(s_plotInterval, self.PlotData)
        self.timerRev = threading.Timer(s_recvInterval, self.RecvData)


    def CalError(self):
        groundForma = [[[8, 0], [16, 0], [24, 0]],      # '一'
                    [[0, -8], [0, -16], [0, -24]],      # '|'
                    [[-8, -8], [8, -8], [0, -16]],      # 棱形
                    [[-8, -8], [8, -8], [0, -8]]]       # 三角形
        
        # 只有运行时才计算误差
        if self.m_toggleBtn2.GetValue():
            formaIndex = self.m_choice3.GetSelection()
            error_1 = ((pos_x[1] - groundForma[formaIndex][0][0]) ** 2 + \
                (pos_y[1] - groundForma[formaIndex][0][1]) ** 2) ** 0.5
            error_2 = ((pos_x[2] - groundForma[formaIndex][1][0]) ** 2 + \
                (pos_y[2] - groundForma[formaIndex][1][1]) ** 2) ** 0.5
            error_3 = ((pos_x[3] - groundForma[formaIndex][2][0]) ** 2 + \
                (pos_y[3] - groundForma[formaIndex][2][1]) ** 2) ** 0.5
        errPos[0].append(error_1)
        errPos[1].append(error_2)
        errPos[2].append(error_3)
        if len(errSam) == 0:
            errSam.append(0)
        else:
            errSam.append(errSam[-1] + 1)


    def RecvData(self):
        ''' 打开串口后，每 20ms检查一次串口缓存，并更新Agent坐标 '''    
        if self.timerRev_running:
            num = s_serialPort.inWaiting()
            if num != 0:
                # 将缓存区数据全部读出
                data = s_serialPort.read(num)
                global pos_x
                global pos_y
                pos_x, pos_y = xbee.DealPosData(pos_x, pos_y, data)
                self.UpdateLocus()
                s_serialPort.reset_input_buffer()
                # 更新当前位置偏差
                self.CalError()
                
            self.timerRev = threading.Timer(s_recvInterval, self.RecvData)
            self.timerRev.start()
        else:
            s_serialPort.close()


    def PlotData(self):
        ''' 绘图函数，包括Agent位置的散点图和各自轨迹 '''

        # 自适应坐标轴范围，每当有 Agent超过当前范围则向其方向移动 20
        if max(pos_x) > MyFrame.posmm.x_max:
            MyFrame.posmm.x_max = max(pos_x)+20
            MyFrame.posmm.x_min = max(pos_x)-80
        elif min(pos_x) < MyFrame.posmm.x_min:
            MyFrame.posmm.x_max = min(pos_x)+80
            MyFrame.posmm.x_min = min(pos_x)-20
        elif max(pos_y) > MyFrame.posmm.y_max:
            MyFrame.posmm.y_max = max(pos_y)+20
            MyFrame.posmm.y_min = max(pos_y)-80
        elif min(pos_y) < MyFrame.posmm.y_min:
            MyFrame.posmm.y_max = min(pos_y)+80
            MyFrame.posmm.y_min = min(pos_y)-20

        self.MPL.cla()
        if self.isShowLocus:
            self.MPL.plotLocus()
        self.MPL.plotScatter(pos_x, pos_y)

        if self.timerPlo_running:
            self.timerPlo = threading.Timer(s_plotInterval, self.PlotData)
            self.timerPlo.start()


    def UpdateLocus(self):
        ''' 每次更新坐标后都要调用UpdateLocus更新轨迹数据，最多保存6000个点 '''
        if(len(MyFrame.locus_x[0]) > 6000):
            del(MyFrame.locus_x[0][0])
            del(MyFrame.locus_x[1][0])
            del(MyFrame.locus_x[2][0])
            del(MyFrame.locus_x[3][0])
            del(MyFrame.locus_y[0][0])
            del(MyFrame.locus_y[1][0])
            del(MyFrame.locus_y[2][0])
            del(MyFrame.locus_y[3][0])
        MyFrame.locus_x[0].append(pos_x[0])
        MyFrame.locus_y[0].append(pos_y[0])
        MyFrame.locus_x[1].append(pos_x[1])
        MyFrame.locus_y[1].append(pos_y[1])
        MyFrame.locus_x[2].append(pos_x[2])
        MyFrame.locus_y[2].append(pos_y[2])
        MyFrame.locus_x[3].append(pos_x[3])
        MyFrame.locus_y[3].append(pos_y[3])


    def showDlgError(self, strInfo):
        ''' 显示错误信息弹窗 '''
        dlg = wx.MessageDialog(self, strInfo, 'ERROR', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


    def OnMousePress(self, event):
        ''' 鼠标双击回调函数，发送目标位置给Leader '''
        if event.dblclick:
            if self.m_toggleBtn1.GetValue() and (not self.m_toggleBtn2.GetValue()):
                xbee.sendLeaderTar(s_serialPort, event.xdata, event.ydata)
                xdata_ = format(event.xdata, '.3f')
                ydata_ = format(event.ydata, '.3f')
                showStr = '[' + time.strftime("%H:%M:%S") + ']>>>向Leader发送目标位置：「x : ' + \
                        xdata_ + ', y : ' + ydata_ +'」\n'
                self.m_textCtrl1.AppendText(showStr)
            else:
                showStr = '[' + time.strftime("%H:%M:%S") + ']>>>当前状态下无法设置目标点' + '\n'
                self.m_textCtrl1.AppendText(showStr)
    

    def OnMouseMotion(self, event):
        ''' plt的鼠标移动回调函数，用于显示当前鼠标所在的坐标位置 '''
        if event.xdata != None:
            xdata_ = format(event.xdata, '.3f')
            ydata_ = format(event.ydata, '.3f')
            self.MPL.ShowHelpString("x=" + xdata_ + ', y=' + ydata_)
        else:
            self.MPL.ShowHelpString("")


    def OnMouseRelease(self, event):
        pass


    def OnFindCOM(self, event):
        ''' 搜索串口的回调函数 '''
        plist = list(list_ports.comports())
        portList = []

        if len(plist)<=0:
            self.m_choice1.SetItems(portList)  
        else:    
            index = 0  
            for ser in plist:  
                plist_0 = list(plist[index])  
                serialName = plist_0[0]  
                portList.append(serialName)  
                index = index+1
            portListTemp = ['       ' + x for x in portList]
            self.m_choice1.SetItems(portListTemp)
        tmpStr = ', '
        showStr = '[' + time.strftime("%H:%M:%S") + ']>>>查找完成，可用串口号：' + \
            tmpStr.join(portList) +'\n'
        self.m_textCtrl1.AppendText(showStr)


    def OnOpenCOM(self, event ):
        ''' 打开/关闭串口的回调函数 '''
        if self.m_toggleBtn1.GetValue():
            index_ = self.m_choice1.GetSelection()
            comPort = self.m_choice1.GetString(index_).lstrip()
            s_serialPort.port = comPort
            index_ = self.m_choice2.GetSelection()
            s_serialPort.baudrate = int(self.m_choice2.GetString(index_).lstrip())
            try:                    # 尝试打开端口
                s_serialPort.open()

                s_serialPort.reset_input_buffer()
                s_serialPort.reset_output_buffer()
                self.timerRev_running = 1
                self.RecvData()

                mChoiceTemp = self.m_choice2.GetString(index_)
                showStr = '[' + time.strftime("%H:%M:%S") + ']>>>打开串口成功，串口号：' +  comPort \
                    + '，波特率：' + mChoiceTemp.lstrip() + '\n'
                self.m_textCtrl1.AppendText(showStr)
                self.m_toggleBtn1.SetLabelText(u"关闭串口")
                self.m_statusBar1.SetStatusText("已连接")
                self.m_choice1.Enable(False)
                self.m_choice2.Enable(False)
                threading.Timer(s_recvInterval, self.RecvData).start()
            except Exception as e:  # 打开当前端口失败
                self.m_toggleBtn1.SetValue(0)

                self.showDlgError('打开串口失败！')
        else:
            self.timerRev_running = 0

            showStr = '[' + time.strftime("%H:%M:%S") + ']>>>关闭串口' + '\n'
            self.m_textCtrl1.AppendText(showStr)
            self.m_toggleBtn1.SetLabelText(u"打开串口")
            self.m_statusBar1.SetStatusText("未连接")
            self.m_choice1.Enable(True)
            self.m_choice2.Enable(True)


    def OnSwitchForma(self, event ):
        ''' 切换队形的回调函数 '''
        if self.m_toggleBtn1.GetValue():
            index_ = self.m_choice3.GetSelection()
            xbee.sendOrderForma(s_serialPort, index_)

            mChoiceTemp = self.m_choice3.GetString(index_)
            showStr = '[' + time.strftime("%H:%M:%S") + ']>>>切换队形：' + \
                mChoiceTemp.lstrip() + '\n'
            self.m_textCtrl1.AppendText(showStr)
        else:
            self.showDlgError('请先连接XBEE！')
    

    def OnStartRunning(self, event ):
        ''' 开始/停止运行的回调函数 '''
        if self.m_toggleBtn1.GetValue():
            if self.m_toggleBtn2.GetValue():
                self.timerPlo_running = 1
                self.PlotData()
                xbee.sendOrderStart(s_serialPort, 1)
                # 每次开始运行时清空误差缓存
                global errPos
                global errSam
                errPos = [[],[],[]]     # 误差
                errSam = []             # 

                showStr = '[' + time.strftime("%H:%M:%S") + ']>>>开始运行...' + '\n'
                self.m_textCtrl1.AppendText(showStr)
                self.m_toggleBtn2.SetLabelText(u"停止运行")
                self.m_statusBar1.SetStatusText("正在运行")
                self.m_button1.Enable(False)
                self.m_toggleBtn1.Enable(False)
            else:
                self.timerPlo_running = 0
                xbee.sendOrderStart(s_serialPort, 0)

                showStr = '[' + time.strftime("%H:%M:%S") + ']>>>停止运行.' + '\n'
                self.m_textCtrl1.AppendText(showStr)
                self.m_toggleBtn2.SetLabelText(u"开始运行")
                self.m_statusBar1.SetStatusText("已连接")
                self.m_button1.Enable(True)
                self.m_toggleBtn1.Enable(True)
        else:
            self.showDlgError('请先连接XBEE！')
            self.m_toggleBtn2.SetValue(0)
    

    def OnReset(self, event ):
        ''' 初始状态的回调函数 '''
        if self.m_toggleBtn2.GetValue():
            self.showDlgError('请先停止运行！')
        else:
            global pos_x
            global pos_y
            pos_x = [0, 8, 16, 24]
            pos_y = [0, 0, 0, 0]
            MyFrame.locus_x = [[], [], [], []]
            MyFrame.locus_y = [[], [], [], []]
            self.PlotData()

            showStr = '[' + time.strftime("%H:%M:%S") + ']>>>恢复初始状态' + '\n' + \
                '    pos_x = [0, 8, 16, 24] \n' + '    pos_y = [0, 0, 0, 0]'
            self.m_textCtrl1.AppendText(showStr)


    def OnShowLocus( self, event ):
        ''' 是否绘制轨迹 '''
        if self.m_checkBox1.GetValue():
            self.isShowLocus = 1
        else:
            self.isShowLocus = 0


    def OnShowError( self, event ):
        self.UpdateUI(2)


    def OnClearBUF( self, event ):
        ''' 清空消息日志缓存 '''
        self.m_textCtrl1.Clear()


class SUBFrame(MyFrame.MyFrame2):
    def __init__(self, parent = None, UpdateUI = None):
        MyFrame.MyFrame2.__init__(self,parent)
        self.icon = wx.Icon('curve.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.UpdateUI = UpdateUI

        self.timerPlo = threading.Timer(0.040, self.PlotErr)
        self.PlotErr()      # 绘制曲线
    

    def PlotErr(self):
        self.MPL.cla()
        self.MPL.plot(errPos[0], errSam, label = 'Agent_2')
        self.MPL.plot(errPos[1], errSam, label = 'Agent_3')
        self.MPL.plot(errPos[2], errSam, label = 'Agent_4')

        self.timerPlo = threading.Timer(0.040, self.PlotErr)
        self.timerPlo.start()