# TCPDeviceClient
### 智能柜python客户端

---
**config.conf配置文件**

    [network]
    #web端url
    website = http://www.mytrystation.com
    #设备管理系统url
    url = http://www.jatool.cn
    #ip
    server = 101.200.231.91
    #端口
    port = 20000

    [device]
    #设备id
    deviceid =
    #版本号
    version = 3.6
    #报警时长（秒）
    givealarmtime = 30
    #报警时间间隔（秒）
    alarminterval = 30
    #开门多长时间报警（秒）
    howtime = 180
    #开锁保持时长
    autolocktime = 8
    #开门状态
    doorclosestatus = 0
    #关门状态
    dooropenstatus = 1
    #开锁状态
    unlockstatus = 0
    #上锁状态
    lockstatus = 1
    #是否录像 1是
    isvideo = 0
    #设备每天检测升级时间段
    programtime = 3

---
**shconfig配置文件**

    #网卡
    netcard=ra0