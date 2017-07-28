#!/usr/bin/env python
#_*_coding:utf-8_*_

import ConfigParser
import os

#获取config配置文件
def getConfig(section, key):
    config = ConfigParser.ConfigParser()
    path = os.path.split(os.path.realpath(__file__))[0] + '/config.conf'
    config.read(path)
    try:
        return config.get(section, key)
    except:
        return False