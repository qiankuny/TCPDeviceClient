#!/usr/bin/env python2.7
#_*_coding:utf-8_*_

import urllib
import urllib2
import json
import time
import os
import hashlib
import mod_config
import logging

class ReportLog(object):
    def __init__(self):
        pass

    def report(self, signal):
        olddirlist = {}
        while True:
            if not signal.is_set():
                break
            if mod_config.getConfig("device", "deviceid"):
                values = {}
                values['enews'] = "get_info"
                values['deviceid'] = mod_config.getConfig("device", "deviceid")#设备id
                data = urllib.urlencode(values)
                # 上报日志的商务系统的网址
                url = mod_config.getConfig("network", "website") + "/api/devicelog.php"
                geturl = url + "?" + data
                try:
                    #先获取服务器上上传的最近的时间
                    request = urllib2.Request(geturl)
                    response = urllib2.urlopen(request)
                    res = json.loads(response.read())
                    if res['status'] == 1:
                        date = res['date']
                    else:
                        date = '2017-01-01 08:00:00'
                    try:
                        for i in os.listdir('log'):
                            if i[0:6] == 'thread':
                                try:
                                    f = open('./log/' + i, 'rb')
                                    md5 = hashlib.md5()
                                    while True:
                                        b = f.read(8096)
                                        if not b:
                                            break
                                        md5.update(b)
                                    filemd5 = md5.hexdigest()
                                    f.close()
                                    if not olddirlist.has_key(i) or olddirlist[i] != filemd5:
                                        try:
                                            f = open('./log/' + i, 'rb')
                                            if f:
                                                key = 0
                                                values = {}
                                                values['enews'] = "post_info"
                                                values['deviceid'] = mod_config.getConfig("device", "deviceid")
                                                logs = {}
                                                for a in f:
                                                    if a[0:19] > date:
                                                        logs[key] = {}
                                                        logs[key]['date'] = a[0:19]
                                                        logs[key]['info'] = a.split(' - ')[2]
                                                        key += 1
                                                values['logs'] = json.dumps(logs)
                                                if logs:
                                                    data = urllib.urlencode(values)
                                                    #上报日志的商务系统的网址
                                                    url = mod_config.getConfig("network", "website") + "/api/devicelog.php"
                                                    try:
                                                        request = urllib2.Request(url, data)
                                                        response = urllib2.urlopen(request)
                                                        res = json.loads(response.read())
                                                        if res['status'] == 1:
                                                            olddirlist[i] = filemd5
                                                            print '日志上报成功'
                                                        else:
                                                            logging.error('日志上报失败')
                                                    except Exception, e:
                                                        logging.error('日志提交失败')
                                                f.close()
                                        except Exception, e:
                                            print '失败'
                                        except IOError:
                                            print '打开文件失败'
                                except Exception, e:
                                    print '失败'
                                except IOError:
                                    print '打开文件失败'
                    finally:
                        if f:
                            f.close()
                except Exception, e:
                    print '没有获取时间'
            time.sleep(60)