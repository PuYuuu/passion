# -*- coding: utf-8 -*- 
# 2021.02.07
# GUI和功能实现部分已基本完成，开学后再把xbee通信帧打包这一部分
# 完成应该就可以用了（谁让你没把xbee通信的东西拷贝一下(→_→)
import time

# 所有XBEE的高8位地址均为0xA2，低8位存储在agentAdd
# A0对应协调器，A1对应leader，A2 A3 A4 分别对应follower 1 2 3
agentAdd = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4]
# 分别对应 ‘一’ ‘|’ ‘口’ ‘棱’形，默认为 ‘一’
agentFor = [0x00, 0x01, 0x02, 0x03]


def DealPosData(x_, y_, data_):
    posx = x_
    posy = y_
    XBEE_RX_BUF = [0] * 30
    XBEE_RX_LEN = 0
    XBEE_RX_FLAG = 0
    XBEE_dataSize = 0

    for i in range(len(data_)):
        # 检测到数据帧帧头
        if data_[i] == 0x7E and XBEE_RX_LEN == 0 and XBEE_RX_FLAG == 0:
            XBEE_RX_FLAG = 1
            XBEE_RX_BUF[0] = 0x7E
            XBEE_RX_LEN = 1
            XBEE_dataSize = 0
        # 将缓存区的数据复制到数据帧数组中
        elif XBEE_RX_FLAG == 1:
            XBEE_RX_BUF[XBEE_RX_LEN] = data_[i]
            XBEE_RX_LEN += 1
            if XBEE_RX_LEN == 3:
                XBEE_dataSize = XBEE_RX_BUF[1] * 256 + XBEE_RX_BUF[2]
                # 如果当前帧在当前缓存区中不完整则直接丢弃
                if i + XBEE_dataSize > len(data_) or XBEE_dataSize > 30:
                    XBEE_RX_LEN = 0
                    XBEE_RX_FLAG = 0
            # 数据帧复制完成
            elif XBEE_RX_LEN > XBEE_dataSize + 3:
                XBEE_RX_FLAG = 2
        
        if XBEE_RX_FLAG == 2:
            # 如果是传送状态回复帧直接跳过
            if XBEE_RX_BUF[3] == 0x89:
                pass
            elif XBEE_RX_BUF[3] == 0x81:        # 数据帧
                # Agent坐标数据
                if XBEE_RX_BUF[8] == 0x01 or XBEE_RX_BUF[8] == 0x00:
                    xTemp = (float)((XBEE_RX_BUF[9] * 256 + XBEE_RX_BUF[10] ) / 500.0)
                    yTemp = (float)((XBEE_RX_BUF[12] * 256 + XBEE_RX_BUF[13] ) / 500.0)
                    if XBEE_RX_BUF[8] == 0x01:
                        xTemp = -xTemp
                    if XBEE_RX_BUF[11] == 0x01:
                        yTemp = -yTemp
                    if XBEE_RX_BUF[5] in agentAdd:
                        posx[agentAdd.index(XBEE_RX_BUF[5]) - 1] = xTemp
                        posy[agentAdd.index(XBEE_RX_BUF[5]) - 1] = yTemp
                elif XBEE_RX_BUF[8] == 0x02:
                    pass
                elif XBEE_RX_BUF[8] == 0x03:
                    pass

            XBEE_RX_LEN = 0
            XBEE_RX_FLAG = 0

    return posx, posy


def xbeeSend(port, add, sendData):
    sendDataBuffer = [0x00] * 15
    sendDataBuffer[0] = 0x7E        # 帧头
    sendDataBuffer[1] = 0x00
    sendDataBuffer[2] = 0x0B        # 帧长 除去帧头帧长和checknum
    sendDataBuffer[3] = 0x01        # 帧类型 16位地址传送帧
    sendDataBuffer[4] = 0x01        # 帧ID 不重要
    sendDataBuffer[5] = 0xA2        # 每个目标地址高位都是A2
    sendDataBuffer[6] = agentAdd[add]   # 目标地址
    sendDataBuffer[7] = 0x01        # Options	Disable ACK
    checkSum = 0xA5 + agentAdd[add]
    for i in range(6):
        sendDataBuffer[8 + i] = sendData[i]
        checkSum += sendData[i]
    # 最后一位为校验位
    sendDataBuffer[14] = 0xFF - (checkSum % 256)
    send = bytearray(sendDataBuffer)
    
    port.write(send)


def sendOrderStart(port, start):
    if start:
        sData = [0x02] * 6
    else:
        sData = [0x03] * 6
    for i in range(5):
        xbeeSend(port, 1, sData)        # 向leader发送开始/停止运动的命令
        time.sleep(0.001)


def sendOrderForma(port, formatID):
    sData = [0x04] * 6
    sData[1] = agentFor[formatID]

    for ad in range(2, 5):
        for i in range(5):
            xbeeSend(port, ad, sData)   # 向3个follower发送切换队形的命令
            time.sleep(0.001)


def sendLeaderTar(port, xdata_, ydata_):
    sData = [0x00] * 6
    xdata = (int)(xdata_ * 500)
    ydata = (int)(ydata_ * 500)
    if xdata < 0:
        xdata = -xdata
        sData[0] = 0x01
    if ydata < 0:
        ydata = -ydata
        sData[3] = 0x01
    sData[1] = xdata // 256
    sData[2] = xdata % 256
    sData[4] = ydata // 256
    sData[5] = ydata % 256

    for i in range(5):
        xbeeSend(port, 1, sData)        # 向leader发送目标位置
        time.sleep(0.001)
     