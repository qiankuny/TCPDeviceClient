#!/usr/bin/env python
# coding: utf-8

import urllib
import urllib2
import time, logging
import tarfile
import os, sys, stat
import shutil
import hashlib
import json
import mod_config

class ProgramUpgrade(object):
    def __init__(self):
        self.realpath = sys.path[0]
        self.tmp = './tmp'
        self.fileurl = ""
        self.localfile = self.tmp + "/updatefile.tar.gz"

    # 计算下载百分比
    def urlcallback(self, a, b, c):
        prec = 100.0 * a * b / c
        if 100 < prec:
            prec = 100
        print "下载%.2f%%" % (prec,)

    # 计算文件MD5
    def getFileMd5(self, filename):
        if not os.path.isfile(filename):
            return
        try:
            mymd5 = hashlib.md5()
            f = open(filename)
            while True:
                b = f.read(8096)
                if not b:
                    break
                mymd5.update(b)
            filemd5 = mymd5.hexdigest()
            f.close()
            return filemd5
        except IOError:
            return

    #目录或文件拼接
    def dirJoinFile(self, a, b):
        if a:
            return os.path.join(a, b)
        else:
            return b

    #遍历更新文件并替换
    def programReplace(self, tmpdir, dir=''):
        # 遍历更新文件
        if os.path.exists(tmpdir):
            for i in os.listdir(tmpdir):
                #判断文件和目录
                if os.path.isfile(os.path.join(tmpdir, i)):
                    # 文件存在先比较
                    if os.path.isfile(self.dirJoinFile(dir, i)):
                        if i != 'config.conf' and i != 'shconfig':
                            filemd5 = self.getFileMd5(os.path.join(tmpdir, i))
                            oldfilemd5 = self.getFileMd5(self.dirJoinFile(dir, i))
                            # 比较新旧文件md5并替换
                            if filemd5 and oldfilemd5 and filemd5 != oldfilemd5:
                                # 没有写权限并修改权限
                                if not os.access(self.dirJoinFile(dir, i), os.W_OK):
                                    try:
                                        os.chmod(os.path.join(self.realpath, self.dirJoinFile(dir, i)), 0o777)
                                    except OSError:
                                        print OSError
                                        return False
                                try:
                                    shutil.copyfile(os.path.join(tmpdir, i), self.dirJoinFile(dir, i))
                                except IOError:
                                    print IOError
                                    return False
                    # 文件不存在之直接拷贝
                    else:
                        try:
                            shutil.copyfile(os.path.join(tmpdir, i), self.dirJoinFile(dir, i))
                        except IOError:
                            print IOError
                            return False
                elif os.path.isdir(os.path.join(tmpdir, i)):
                    if not os.path.exists(self.dirJoinFile(dir, i)):
                        os.mkdir(self.dirJoinFile(dir, i))
                    self.programReplace(os.path.join(tmpdir, i), self.dirJoinFile(dir, i))
        return True

    #下载更新文件
    def programDownload(self, signal):
        if not signal.is_set():#检测升级线程是否终止
            return False
        if os.path.exists(self.tmp):
            #目录存在清除
            try:
                shutil.rmtree(self.tmp)
            except:
                return False
        #创建目录
        try:
            os.mkdir(self.tmp)
        except OSError,e:
            print e
            return False
        url = self.fileurl
        local = self.localfile
        #下载更新文件压缩包
        try:
            urllib.urlretrieve(url, local, self.urlcallback)
        except urllib.ContentTooShortError:
            return self.programDownload(signal)
        except IOError:
            return False
        if not signal.is_set():#下载完检测升级线程是否终止
            return False
        #将更新文件压缩包解压到目录
        try:
            tar = tarfile.open(local)
            tar.extractall(self.tmp)
            tar.close()
        except:
            return False
        else:
            if not signal.is_set():#解压缩完检测升级线程是否终止
                return False
            return True

    def main(self, signal):
        while True:
            if not signal.is_set():#检测升级线程是否终止
                break
            # 判断是否有设备id、是否到了检测升级的时间，programtime是要检测升级的时间
            if mod_config.getConfig("device", "deviceid") and int(time.strftime('%H', time.localtime(time.time()))) == int(mod_config.getConfig("device", "programtime")):
                values = {}
                values['route'] = "api/swupdate/upgradeInfo"
                values['deviceid'] = mod_config.getConfig("device", "deviceid")#设备id
                data = urllib.urlencode(values)
                #设备管理系统网址
                url = mod_config.getConfig("network", "url") + "/index.php"
                geturl = url + "?" + data
                try:
                    request = urllib2.Request(geturl)
                    response = urllib2.urlopen(request)
                    res = json.loads(response.read())
                    #判断是否要升级
                    if int(res['status']):
                        self.fileurl = mod_config.getConfig("network", "url") + "/download/" + res['filename']
                        version = res['version']
                        if self.programDownload(signal):
                            if self.programReplace(self.tmp):
                                values = {}
                                values['deviceid'] = mod_config.getConfig("device", "deviceid")
                                values['version'] = version
                                data = urllib.urlencode(values)
                                url = mod_config.getConfig("network", "url") + "/index.php?route=api/swupdate/updated"
                                try:
                                    request = urllib2.Request(url, data)
                                    response = urllib2.urlopen(request)
                                    res = json.loads(response.read())
                                    if res['status'] == 1:
                                        mod_config.setConfig("device", "version", version)
                                        if os.path.exists(self.tmp):
                                            # 目录存在清除
                                            shutil.rmtree(self.tmp)
                                        logging.info('设备升级到%s', str(version))
                                        os.system('reboot -f')
                                    else:
                                        logging.error('升级上报失败')
                                except Exception, e:
                                    logging.error('升级提交失败')
                finally:
                    pass
            time.sleep(600)