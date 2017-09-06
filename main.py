#!/usr/bin/env python2.7
#_*_coding:utf-8_*_

import TCPConnection
import ReportLog
import socket, time, struct, threading
import uuid
import inspect
import ctypes
import logging
from logging.handlers import TimedRotatingFileHandler
import re
import sys, os
import mod_config
import ProgramUpgrade

def daemonize(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) $s\n" % (e.errno, e.strerror))
        sys.exit(1)
    os.chdir("/opt/TCPDeviceClient/")
    os.umask(0)
    os.setsid()
    try:
       pid = os.fork()
       if pid > 0:
           sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    for f in sys.stdout, sys.stderr: f.flush()
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

def init_logging():
    logger = logging.getLogger()
    if True == __debug__:
        logger.setLevel(logging.DEBUG)  # Log等级总开关
    else:
        logger.setLevel(logging.INFO)  # Log等级总开关
    formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d][threadName:%(threadName)s,thread:%(thread)d] - %(levelname)s: %(message)s')  # 每行日志的前缀设置
    fth = TimedRotatingFileHandler(filename="./log/thread", when="D", interval=1, backupCount=7)
    sh = logging.StreamHandler()
    fth.suffix = "%Y%m%d.log"  # 设置 切分后日志文件名的时间格式 默认 filename+"." + suffix
    fth.extMatch = re.compile(r"^\d{4}\d{2}\d{2}.log$")
    fth.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fth)
    logger.addHandler(sh)

if __name__ == "__main__":
    daemonize('/dev/null', '/tmp/daemon_stdout.log', '/tmp/daemon_error.log')
    init_logging()
    while True:
        time.sleep(1)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            try:
                sock.connect((mod_config.getConfig("network", "server"), int(mod_config.getConfig("network", "port"))))
            except Exception, e:
                sock.close()
                logging.error('socket连接异常: %s', e)
                continue
            sockname = sock.getsockname()
            tcpc = TCPConnection.TCPConnection(sock, sockname[0], mod_config.getConfig("device", "deviceid"), sockname[1])
            try:
                loginresult = tcpc.login()
            except Exception, e:
                sock.close()
                logging.error('登录异常: %s', e)
                continue
            if loginresult == 0:
                signal = threading.Event()
                signal.set()
                # 检测握手心跳
                sh = threading.Thread(target=tcpc.shakeHand)
                sh.start()
                # 检查开门并上报门磁状态
                ds = threading.Thread(target=tcpc.reportDoorStatus)
                ds.start()
                tr = threading.Thread(target=tcpc.threadRecv)
                tr.start()
                logging.info('start %s', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
                # 上报日志线程
                report = ReportLog.ReportLog()
                re = threading.Thread(target=report.report, args=(signal,))
                re.start()
                # 更新程序
                program = ProgramUpgrade.ProgramUpgrade()
                pu = threading.Thread(target=program.main, args=(signal,))
                pu.start()
                while True:
                    try:
                        if tcpc.socketreconnect == 0:
                            signal.clear()
                            sock.close()
                            break
                    except:
                        signal.clear()
                        sock.close()
                        break
            elif loginresult == 1:
                sock.close()
                logging.error('拒绝登录')
                continue
            else:
                sock.close()
                logging.error('协议版本号错误')
                continue
        except Exception, e:
            logging.error('异常: %s', e)