#!/usr/bin/env python2.7
#_*_coding:utf-8_*_

import logging, time, threading
import os
import socket
from protocol_m import StructBase as sb
from protocol_m import TransferProtocol as tp
from protocol_m import ErrorCode
import ctypes as ct
import mod_config
import json

class TCPConnection(object):
    def __init__(self, sock, deviceip, deviceid, listenport):
        self.sock = sock
        self.deviceip = deviceip
        self.deviceid = deviceid
        self.listenport = listenport
        self.lock = threading.Lock()
        self.givealarmtime = int(mod_config.getConfig("device", "givealarmtime")) #告警时长
        self.isgivealarm = 0 #是否正在告警，1：正在告警
        self.sendshakehand = 0 #是否正在发送握手，1：正在发送
        self.socketreconnect = 1 #socket是否重连，0：重连
        self.autolocktime = int(mod_config.getConfig("device", "autolocktime")) #开锁后多次时间不开门自动上锁计时器
        self.resetautolock = time.time() #重置标记自动开锁时间戳

    #登录
    def login(self):
        head = tp.MsgHead()
        head.iMsgType = tp.MsgTypeEnum.LOGIN_AUTH
        head.iSubMsgType = tp.MsgSubTypeEnum.REQUEST
        head.iPayloadLen = ct.sizeof(tp.MsgHead) + ct.sizeof(tp.LoginAuth)
        head.iFeedBack = 1
        login = tp.LoginAuth()
        login.cDeviceID = self.deviceid
        login.cVersion = mod_config.getConfig("device", "version")#版本号
        login.cDeviceIP = self.deviceip
        login.iListenPort = self.listenport
        self.sock.sendall(head.pack() + login.pack())
        msg_header = list()
        while True:
            data = self.sock.recv(1)
            if data != None and len(data) == 1:
                msg_header.append(data)
                if len(msg_header) == ct.sizeof(tp.MsgHead):
                    msgHead = tp.MsgHead.unpack(b''.join(msg_header))
                    if True == msgHead.testCheckSum():
                        msg_header = list()
                        dataLength = msgHead.iPayloadLen - ct.sizeof(tp.MsgHead)
                        data = self.sock.recv(dataLength)
                        msg_header.append(data)
                        break
                        # print "iMsgType:%08x,iSubMsgType:%08x,dataLength: %s" % (msgHead.iMsgType, msgHead.iSubMsgType, dataLength)
            else:
                break
        msgbody = tp.Result.unpack(b''.join(msg_header))
        return msgbody.iResult

    #数据发送加锁
    def sockSend(self, data, sendshakehand = 0):
        self.lock.acquire()
        if self.sendshakehand ==  0:
            if sendshakehand != 0:
                self.sendshakehand = 1
            try:
                self.sock.sendall(data)
            except socket.error, e:
                logging.error('socket发送错误: %s', e)
                self.socketreconnect = 0
            except socket.timeout, e:
                logging.error('发送超时: %s', e)
                self.socketreconnect = 0
            finally:
                self.lock.release()
            self.sendshakehand = 0
        else:
            time.sleep(0.1)
            self.sockSend(data, sendshakehand)

    #握手心跳
    def shakeHand(self):
        head = tp.MsgHead()
        head.iMsgType = tp.MsgTypeEnum.SHAKE_HAND
        head.iSubMsgType = tp.MsgSubTypeEnum.UNUSED
        head.iPayloadLen = ct.sizeof(tp.MsgHead)
        head.iFeedBack = 0
        while self.socketreconnect:
            # self.sock.send(head.pack())
            self.sockSend(head.pack(), 1)
            time.sleep(10)

    #检查开门并上报门磁状态
    def reportDoorStatus(self):
        y = 0
        howtime = int(mod_config.getConfig("device", "howtime")) #多长时间报警
        alarminterval = int(mod_config.getConfig("device", "alarminterval")) #报警间隔时间
        opentime = time.time() #开门的时间
        while self.socketreconnect:
            try:
                arrs = []
                n = 0
                while n < 10:
                    gp = os.popen('cat /dev/gpio-P1.7')
                    p = gp.read()
                    gp.close()
                    if p:
                        n = n + 1
                        arrs.append(int(p[0]))
                    time.sleep(0.01)
                if 0 in arrs:
                    x = int(mod_config.getConfig("device", "doorclosestatus"))#关门状态
                else:
                    x = int(mod_config.getConfig("device", "dooropenstatus"))#开门状态
                if y != x:
                    y = x
                    head = tp.MsgHead()
                    head.iMsgType = tp.MsgTypeEnum.STATUS_REPORT
                    head.iSubMsgType = tp.MsgSubTypeEnum.UNUSED
                    head.iPayloadLen = ct.sizeof(tp.MsgHead) + ct.sizeof(tp.ControllerStatus)
                    head.iFeedBack = 1
                    status = tp.ControllerStatus()
                    status.iInputStatus[0] = ct.c_int32(y)
                    status.iOutputStatus[0] = ct.c_int32(y)
                    # self.sock.send(head.pack() + status.pack())
                    self.sockSend(head.pack() + status.pack())
                    if y == 1:
                        opentime = time.time()
                    os.system('echo '+str(mod_config.getConfig("device", "lockstatus"))+' > /dev/gpio-P1.24')  # 上锁
                    if y == 0 and self.isgivealarm == 1 and self.givealarmtime >= 1:
                        self.givealarmtime = 0
                    if int(mod_config.getConfig("device", "isvideo")) == 1:#是否录像
                        if y == 1:
                            uitime = time.time()
                            filename = time.strftime("%Y%m%d%H%M%S", time.localtime(uitime))
                            os.system('openRTSP -t -F "/media/sd-mmcblk0p1/' + filename + '." "rtsp://192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?real_stream" &')
                            self.giveAlarm(3, 4, 3, int(uitime))
                        else:
                            rtsp = os.popen("ps | grep 'openRTSP -t -F /media/sd-mmcblk0p1/' | grep -v grep | awk '{print $1}'")
                            pid = rtsp.read()
                            rtsp.close()
                            if pid:
                                os.system('kill -HUP ' + pid)
                else:
                    currenttime = time.time()
                    if self.isgivealarm == 0 and x == 1 and (int(currenttime - opentime) == howtime or (int(currenttime - opentime) > howtime and int(currenttime - opentime) % (self.givealarmtime + alarminterval) == 0)): #开门时间太久
                        ga = threading.Thread(target=self.openDoorLongGiveAlarm)
                        ga.start()
            except Exception, e:
                logging.error(e)
                continue

    #告警或录像上报
    def giveAlarm(self, type, subtype, level, uitime = int(time.time())):
        head = tp.MsgHead()
        head.iMsgType = tp.MsgTypeEnum.ALARM_REPORT
        head.iSubMsgType = tp.MsgSubTypeEnum.UNUSED
        head.iPayloadLen = ct.sizeof(tp.MsgHead) + ct.sizeof(tp.AlarmStruct)
        head.iFeedBack = 1
        alarm = tp.AlarmStruct()
        alarm.cType = type
        alarm.cSubType = subtype
        alarm.cLevel = level
        alarm.uiTime = uitime
        self.sockSend(head.pack() + alarm.pack())

    #开门时间过久告警
    def openDoorLongGiveAlarm(self):
        if self.isgivealarm == 0:
            n = self.givealarmtime
            self.isgivealarm = 1
            startalarmtime = time.time()
            head = tp.MsgHead()
            head.iMsgType = tp.MsgTypeEnum.ALARM_REPORT
            head.iSubMsgType = tp.MsgSubTypeEnum.UNUSED
            head.iPayloadLen = ct.sizeof(tp.MsgHead) + ct.sizeof(tp.AlarmStruct)
            head.iFeedBack = 1
            alarm = tp.AlarmStruct()
            alarm.cType = 1
            alarm.cSubType = 3
            alarm.cLevel = 3
            alarm.uiTime = int(time.time())
            self.sockSend(head.pack() + alarm.pack())
            while self.givealarmtime > 0:
                os.system('echo 1 > /sys/class/leds/beep/brightness')
                time.sleep(0.1)
                os.system('echo 0 > /sys/class/leds/beep/brightness')
                time.sleep(0.1)
                if time.time() - startalarmtime > self.givealarmtime:
                    self.givealarmtime = 0
            self.givealarmtime = n
            self.isgivealarm = 0

    def threadRecv(self):
        msg_header = list()
        shake_hand_time = time.time()
        while self.socketreconnect:
            if time.time() - shake_hand_time > 20:#获取反馈握手包超时
                self.socketreconnect = 0
                logging.error('没有获取反馈握手包，握手中断')
                continue
            try:
                data = self.sock.recv(1)
            except:
                continue
            if data != None and len(data) == 1:
                msg_header.append(data)
                if len(msg_header) == ct.sizeof(tp.MsgHead):
                    msgHead = tp.MsgHead.unpack(b''.join(msg_header))
                    if True == msgHead.testCheckSum():
                        if msgHead.iMsgType == tp.MsgTypeEnum.SHAKE_HAND:#获取握手包
                            shake_hand_time = time.time()
                        msg_header = list()
                        dataLength = msgHead.iPayloadLen - ct.sizeof(tp.MsgHead)
                        try:
                            data = self.sock.recv(dataLength)
                        except:
                            continue
                        msg_header.append(data)
                        if msgHead.iMsgType == tp.MsgTypeEnum.DEVICE_CONTROL: #设备控制
                            msgbody = tp.RemoteOpenDoorParam.unpack(b''.join(msg_header))
                            if msgbody.iIndex == 0:
                                if msgHead.iSubMsgType == tp.DeviceControlTypeEnum.REMOTE_OPENDOOR_COMMAND: #开锁
                                    unlock = threading.Thread(target=self.openDoorUnlock)
                                    unlock.start()
                        elif msgHead.iMsgType == tp.MsgTypeEnum.ALIVE: #在线查询
                            head = tp.MsgHead()
                            head.iMsgType = tp.MsgTypeEnum.ALIVE
                            head.iSubMsgType = tp.MsgSubTypeEnum.UNUSED
                            head.iPayloadLen = ct.sizeof(tp.MsgHead)
                            head.iFeedBack = 0
                            self.sockSend(head.pack())
                        elif msgHead.iMsgType == tp.MsgTypeEnum.STATUS_REPORT:
                            msgbody = tp.ControllerStatus.unpack(b''.join(msg_header))
                            print msgbody.iInputStatus
                            print msgbody.iOutputStatus
                        elif msgHead.iMsgType == tp.MsgTypeEnum.TEMPERATURE_MODE:
                            msgbody = tp.TemperatureModeStruct.unpack(b''.join(msg_header))
                            print msgbody.uiMode
                        msg_header = list()
                        # logging.info("iMsgType:%08x,iSubMsgType:%08x,dataLength: %s" % (msgHead.iMsgType, msgHead.iSubMsgType, dataLength))

    #开门锁
    def openDoorUnlock(self):
        os.system('echo 1 > /sys/class/leds/beep/brightness')
        time.sleep(0.2)
        os.system('echo 0 > /sys/class/leds/beep/brightness')
        time.sleep(0.1)
        os.system('echo 1 > /sys/class/leds/beep/brightness')
        time.sleep(0.2)
        os.system('echo 0 > /sys/class/leds/beep/brightness')
        os.system('echo '+str(mod_config.getConfig("device", "unlockstatus"))+' > /dev/gpio-P1.24')#开锁
        self.autolocktime = int(mod_config.getConfig("device", "autolocktime"))#开锁保持时长
        self.resetautolock = resetautolock = time.time()#标记最新开锁时间
        head = tp.MsgHead()
        head.iMsgType = tp.MsgTypeEnum.DEVICE_CONTROL
        head.iSubMsgType = tp.DeviceControlTypeEnum.REMOTE_OPENDOOR_COMMAND
        head.iPayloadLen = ct.sizeof(tp.MsgHead) + ct.sizeof(tp.Result)
        head.iFeedBack = 0
        result = tp.Result()
        result.iResult = 1
        # self.sock.send(head.pack() + result.pack())
        self.sockSend(head.pack() + result.pack())
        self.outLockStatusReport(1)
        while self.autolocktime > 0:
            if resetautolock != self.resetautolock:
                break
            self.autolocktime = self.autolocktime - 1
            time.sleep(1)
        if resetautolock == self.resetautolock:
            os.system('echo '+str(mod_config.getConfig("device", "lockstatus"))+' > /dev/gpio-P1.24')#上锁
            self.outLockStatusReport(0)

    #锁状态上报
    def outLockStatusReport(self, data):
        data = int(data)
        head = tp.MsgHead()
        head.iMsgType = tp.MsgTypeEnum.STATUS_REPORT
        head.iSubMsgType = tp.MsgSubTypeEnum.UNUSED
        head.iPayloadLen = ct.sizeof(tp.MsgHead) + ct.sizeof(tp.ControllerStatus)
        head.iFeedBack = 1
        status = tp.ControllerStatus()
        try:
            arrs = []
            n = 0
            while n < 10:
                gp = os.popen('cat /dev/gpio-P1.7')
                p = gp.read()
                gp.close()
                if p:
                    n = n + 1
                    arrs.append(int(p[0]))
                time.sleep(0.01)
            if 0 in arrs:
                x = int(mod_config.getConfig("device", "doorclosestatus"))#关门状态
            else:
                x = int(mod_config.getConfig("device", "dooropenstatus"))#开门状态
            status.iInputStatus[0] = ct.c_int32(x)
            if data == 1:
                status.iOutputStatus[0] = ct.c_int32(1)
            else:
                if x == 1:
                    status.iOutputStatus[0] = ct.c_int32(1)
                else:
                    status.iOutputStatus[0] = ct.c_int32(0)
        except Exception, e:
            status.iOutputStatus[0] = ct.c_int32(data)
            status.iInputStatus[0] = ct.c_int32(0)
            logging.error('读取gpio-P1.7出错', e)
        self.sockSend(head.pack() + status.pack())
