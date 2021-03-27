# -*- coding: utf-8 -*- 

import wx
import wx.xrc

import matplotlib
# matplotlib采用WXAgg为后台,将matplotlib嵌入wxPython中
matplotlib.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.ticker import MultipleLocator


class POSM_M():
    def __init__(self):
        self.x_min = -50
        self.x_max = 50
        self.y_min = -50
        self.y_max = 50

posmm = POSM_M()
locus_x = [[], [], [], []]
locus_y = [[], [], [], []]
######################################################################################
class MPL_Panel_base(wx.Panel):
    ''' MPL_Panel_base面板,可以继承或者创建实例'''

    def __init__(self, parent, panel_, boxer_):
        wx.Panel.__init__(self, parent=parent)
        self.boxer = boxer_
        self.panel = panel_

        self.Figure = matplotlib.figure.Figure()
        self.axes = self.Figure.add_axes([0.1, 0.1, 0.8, 0.8])
        self.FigureCanvas = FigureCanvas(self.panel, -1, self.Figure)

        self.NavigationToolbar = NavigationToolbar(self.FigureCanvas)
        self.StaticText = wx.StaticText(self.panel, -1, label='')
		
        self.SubBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SubBoxSizer.Add(self.NavigationToolbar, proportion=0, border=2, flag=wx.ALL | wx.EXPAND)
        self.SubBoxSizer.Add(self.StaticText, proportion=-1, border=2, flag=wx.ALL | wx.EXPAND)

        self.TopBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.TopBoxSizer.Add(self.FigureCanvas, proportion=20, border=0, flag=wx.ALL | wx.EXPAND)
        self.TopBoxSizer.Add(self.SubBoxSizer, proportion=1, border=0, flag=wx.ALL | wx.EXPAND)
        # self.TopBoxSizer.Add(self.FigureCanvas, proportion=10, border=0, flag=wx.ALL | wx.EXPAND)

        self.boxer.Add(self.TopBoxSizer, 1, wx.ALL | wx.EXPAND, 0)


    def UpdatePlot(self):
        ''' 修改图形的任何属性后都必须使用self.UpdatePlot()更新GUI界面 '''
        self.FigureCanvas.draw()


    def plot(self, *args, **kwargs):
        ''' 最常用的绘图命令plot '''
        self.axes.plot(*args, **kwargs)


    def plotLocus(self):
        ''' 绘制 Agent轨迹 '''
        # 轨迹颜色分别为黑色、红色、绿色和蓝色
        color_ = ['k', 'r', 'g', 'b']

        self.axes.plot(locus_x[0], locus_y[0], color_[0])
        self.axes.plot(locus_x[1], locus_y[1], color_[1])
        self.axes.plot(locus_x[2], locus_y[2], color_[2])
        self.axes.plot(locus_x[3], locus_y[3], color_[3])
	

    def plotScatter(self, *args):
        ''' 绘制散点图，即 Agent位置 '''
        x_ = args[0]
        y_ = args[1]
        color_ = ['k', 'r', 'g', 'b']
        label_ = ['Agent_1','Agent_2','Agent_3','Agent_4']
        self.plotBase()
        # self.axes.scatter(*args, marker='s', s = 32, c = color_)
        self.axes.scatter(x_[0], y_[0], label = label_[0], marker='s', s = 32, c = color_[0])
        self.axes.scatter(x_[1], y_[1], label = label_[1], marker='s', s = 32, c = color_[1])
        self.axes.scatter(x_[2], y_[2], label = label_[2], marker='s', s = 32, c = color_[2])
        self.axes.scatter(x_[3], y_[3], label = label_[3], marker='s', s = 32, c = color_[3])
        self.axes.legend()
        self.UpdatePlot()

    def plotBase(self):
        self.xlim(posmm.x_min, posmm.x_max)
        self.ylim(posmm.y_min, posmm.y_max)
        self.xticker(10, 10)
        self.yticker(10, 10)
        self.grid()

    def grid(self, flag=True):
        ''' 显示网格 '''
        if flag:
            self.axes.grid()
        else:
            self.axes.grid(False)

    def title_MPL(self, TitleString="wxMatPlotLib Example In wxPython"):
        ''' 给图像添加一个标题   '''
        self.axes.set_title(TitleString)

    def xlabel(self, XabelString="X"):
        ''' Add xlabel to the plotting    '''
        self.axes.set_xlabel(XabelString)

    def ylabel(self, YabelString="Y"):
        ''' Add ylabel to the plotting '''
        self.axes.set_ylabel(YabelString)

    def xticker(self, major_ticker=1.0, minor_ticker=0.1):
        ''' 设置X轴的刻度大小 '''
        self.axes.xaxis.set_major_locator(MultipleLocator(major_ticker))
        self.axes.xaxis.set_minor_locator(MultipleLocator(minor_ticker))

    def yticker(self, major_ticker=1.0, minor_ticker=0.1):
        ''' 设置Y轴的刻度大小 '''
        self.axes.yaxis.set_major_locator(MultipleLocator(major_ticker))
        self.axes.yaxis.set_minor_locator(MultipleLocator(minor_ticker))

    def legend(self, *args, **kwargs):
        ''' 图例legend for the plotting  '''
        self.axes.legend(*args, **kwargs)

    def xlim(self, x_min, x_max):
        ''' 设置x轴的显示范围  '''
        self.axes.set_xlim(x_min, x_max)

    def ylim(self, y_min, y_max):
        ''' 设置y轴的显示范围   '''
        self.axes.set_ylim(y_min, y_max)

    def savefig(self, *args, **kwargs):
        ''' 保存图形到文件 '''
        self.Figure.savefig(*args, **kwargs)

    def cla(self):
        ''' 再次画图前,必须调用该命令清空原来的图形  '''
        self.axes.clear()
        self.Figure.set_canvas(self.FigureCanvas)

    def ShowHelpString(self, HelpString="Show Help String"):
        ''' 可以用它来显示一些帮助信息,如鼠标位置等 '''
        self.StaticText.SetLabel(HelpString)


class MyFrame1 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Passion", pos = wx.DefaultPosition, \
			size = wx.Size( 1000,700 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )
		
		bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sbSizer1 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel1, wx.ID_ANY, u"绘制区域" ), wx.VERTICAL )
		
		self.MPL = MPL_Panel_base(self, self.m_panel1, sbSizer1)
		x_ = [0, 8, 16, 24]
		y_ = [0, 0, 0, 0]
		self.MPL.cla()
		self.MPL.plotScatter(x_, y_)

		self.m_panel1.SetSizer( sbSizer1 )
		self.m_panel1.Layout()
		sbSizer1.Fit( self.m_panel1 )
		bSizer1.Add( self.m_panel1, 3, wx.EXPAND |wx.ALL, 10 )
		
		
		self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel2, wx.ID_ANY, u"控制面板" ), wx.VERTICAL )
		
		gSizer1 = wx.GridSizer( 0, 2, 0, 0 )
		
		m_choice1Choices = []
		self.m_choice1 = wx.Choice( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, 0 )
		self.m_choice1.SetSelection( 0 )
		self.m_choice1.SetToolTip( u"端口号" )
		gSizer1.Add( self.m_choice1, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button1 = wx.Button( sbSizer2.GetStaticBox(), wx.ID_ANY, u"搜索串口", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button1, 1, wx.ALL|wx.EXPAND, 5 )
		
		m_choice2Choices = [ u"        2400", u"        4800", u"        9600", u"       19200", \
                    u"       38400", u"      115200" ]
		self.m_choice2 = wx.Choice( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice2Choices, 0 )
		self.m_choice2.SetSelection( 0 )
		self.m_choice2.SetToolTip( u"波特率" )
		gSizer1.Add( self.m_choice2, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_toggleBtn1 = wx.ToggleButton( sbSizer2.GetStaticBox(), wx.ID_ANY, u"打开串口", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_toggleBtn1, 1, wx.ALL|wx.EXPAND, 5 )
		
		m_choice3Choices = [ u"       ”一“形", u"       ”|“形", u"       ”棱“形", u"       ”口“形" ]
		self.m_choice3 = wx.Choice( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice3Choices, 0 )
		self.m_choice3.SetSelection( 0 )
		gSizer1.Add( self.m_choice3, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button2 = wx.Button( sbSizer2.GetStaticBox(), wx.ID_ANY, u"切换队形", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button2, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_toggleBtn2 = wx.ToggleButton( sbSizer2.GetStaticBox(), wx.ID_ANY, u"开始运行", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_toggleBtn2, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button3 = wx.Button( sbSizer2.GetStaticBox(), wx.ID_ANY, u"初始状态", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button3, 1, wx.ALL|wx.EXPAND, 5 )
		
		# self.m_staticText2 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		# self.m_staticText2.Wrap( -1 )
		# gSizer1.Add( self.m_staticText2, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_checkBox1 = wx.CheckBox( sbSizer2.GetStaticBox(), wx.ID_ANY, u"显示轨迹", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_checkBox1, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_button5 = wx.Button( sbSizer2.GetStaticBox(), wx.ID_ANY, u"误差曲线", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer1.Add( self.m_button5, 1, wx.ALL|wx.EXPAND, 5 )
		
		sbSizer2.Add( gSizer1, 1, wx.EXPAND, 10 )
		
		bSizer2.Add( sbSizer2, 1, wx.EXPAND, 10 )
		
		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel2, wx.ID_ANY, u"消息日志" ), wx.VERTICAL )
		
		self.m_textCtrl1 = wx.TextCtrl( sbSizer3.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
		sbSizer3.Add( self.m_textCtrl1, 5, wx.ALL|wx.EXPAND, 5 )
		
		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText1 = wx.StaticText( sbSizer3.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )
		bSizer3.Add( self.m_staticText1, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_button4 = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"清空缓存", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button4, 1, wx.ALL, 5 )
		
		
		sbSizer3.Add( bSizer3, 1, wx.EXPAND, 5 )
		
		bSizer2.Add( sbSizer3, 2, wx.EXPAND, 10 )
		
		
		self.m_panel2.SetSizer( bSizer2 )
		self.m_panel2.Layout()
		bSizer2.Fit( self.m_panel2 )
		bSizer1.Add( self.m_panel2, 1, wx.EXPAND |wx.ALL, 10 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		self.m_statusBar1 = self.CreateStatusBar( 1, wx.STB_DEFAULT_STYLE, wx.ID_ANY )
		self.m_statusBar1.SetStatusText("未连接")
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.MPL.FigureCanvas.mpl_connect('motion_notify_event', self.OnMouseMotion)
		self.MPL.FigureCanvas.mpl_connect('button_press_event', self.OnMousePress)
		self.MPL.FigureCanvas.mpl_connect('button_release_event', self.OnMouseRelease)
		self.m_button1.Bind( wx.EVT_BUTTON, self.OnFindCOM )
		self.m_toggleBtn1.Bind( wx.EVT_TOGGLEBUTTON, self.OnOpenCOM )
		self.m_button2.Bind( wx.EVT_BUTTON, self.OnSwitchForma )
		self.m_toggleBtn2.Bind( wx.EVT_TOGGLEBUTTON, self.OnStartRunning )
		self.m_button3.Bind( wx.EVT_BUTTON, self.OnReset )
		self.m_checkBox1.Bind( wx.EVT_CHECKBOX, self.OnShowLocus )
		self.m_button5.Bind( wx.EVT_BUTTON, self.OnShowError )
		self.m_button4.Bind( wx.EVT_BUTTON, self.OnClearBUF )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnMouseMotion(self, event):
		''' plt的鼠标移动回调函数，用于显示当前鼠标所在的坐标位置 '''
		pass

	def OnMousePress(self, event):
		''' plt的鼠标按键按下回调函数 '''
		pass

	def OnMouseRelease(self, event):
		''' plt的鼠标按键释放回调函数 '''
		pass
	
	def OnFindCOM( self, event ):
		event.Skip()
	
	def OnOpenCOM( self, event ):
		event.Skip()
	
	def OnSwitchForma( self, event ):
		event.Skip()
	
	def OnStartRunning( self, event ):
		event.Skip()
	
	def OnReset( self, event ):
		event.Skip()
	    
	def OnShowLocus( self, event ):
		event.Skip()

	def OnShowError( self, event ):
		event.Skip()

	def OnClearBUF( self, event ):
		event.Skip()	



class MyFrame2 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Passion", pos = wx.DefaultPosition, size = wx.Size( 450,450 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )
		
		bSizer4 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_panel3 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sbSizer4 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel3, wx.ID_ANY, u"编队误差曲线" ), wx.VERTICAL )
		
		self.MPL = MPL_Panel_base(self, self.m_panel3, sbSizer4)
		self.MPL.plot()
		
		self.m_panel3.SetSizer( sbSizer4 )
		self.m_panel3.Layout()
		sbSizer4.Fit( self.m_panel3 )
		bSizer4.Add( self.m_panel3, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer4 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass