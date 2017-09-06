#!/bin/sh
. /opt/TCPDeviceClient/shconfig

#添加log
writelog(){
    curtime=`date +"%Y-%m-%d %H:%M:%S"`
    echo $curtime" - shell - "$1 >> /opt/TCPDeviceClient/log/thread
}

sleep 60
pc=0
while :
do
    ra=`ifconfig | grep ${netcard} | grep -v grep | awk '{print $1}'`
    if [ -z $ra ]
    then
        writelog "${netcard}丢失"
        #临时解决 ra0丢失后重启系统
        writelog "${netcard}丢失后重启系统"
        reboot -f

        pid=`ps | grep wpa_supplicant | grep 'wpa_supplicant -B -Dwext -i${netcard} -c /etc/wpa_supplican' | grep -v grep | awk '{print $1}'`
        if test $pid
        then
            writelog "自动杀死wpa_supplicant进程"
            kill -9 $pid
        fi
        pid=`ps | grep udhcpc | grep 'udhcpc -i ${netcard}' | grep -v grep | awk '{print $1}'`
        if test $pid
        then
            writelog "自动杀死udhcpc进程"
            kill -9 $pid
        fi
        if [ -e /var/run/wpa_supplicant/${netcard} ]
        then
            writelog "如果/var/run/wpa_supplicant/${netcard}存在将其删除"
            rm /var/run/wpa_supplicant/${netcard}
        fi
        sleep 10
        ssid=`cat /etc/wpa_supplicant.conf | grep ssid=\" | cut -d "=" -f2`
        while :
        do
            ifconfig ${netcard} up
            writelog "重新up ${netcard}"
            ra=`ifconfig | grep ${netcard} | grep -v grep | awk '{print $1}'`
            if [ $ra ]
            then
                break
            fi
			sleep 1
        done
        while :
        do
            getwifi=`iwlist ${netcard} scanning | grep $ssid | grep -v grep`
            writelog "获取无线网卡数据"
            if test $getwifi
            then
                break
            fi
            sleep 1
        done
        wpa_supplicant -B -Dwext -i${netcard} -c /etc/wpa_supplicant.conf -d
        writelog "重新加载wpa_supplicant"
        while :
        do
            sleep 1
            pid=`ps | grep wpa_supplicant | grep 'wpa_supplicant -B -Dwext -i${netcard} -c /etc/wpa_supplican' | grep -v grep | awk '{print $1}'`
            if test $pid
            then
                break
            fi
        done
        udhcpc -i ${netcard}
        writelog "重新加载udhcpc"
        while :
        do
            sleep 1
            pid=`ps | grep udhcpc | grep 'udhcpc -i ${netcard}' | grep -v grep | awk '{print $1}'`
            if test $pid
            then
                break
            fi
        done
        pid=`ps | grep python | grep /opt/TCPDeviceClient/main.py | grep -v grep | awk '{print $1}'`
        if test $pid
        then
            writelog "杀死主程序进程"
            kill -9 $pid
        fi
    fi

    ping -c 1 61.135.169.125 > /dev/null 2>&1
    if [ $? -eq 0 ];then
        status=`ps | grep python | grep /opt/TCPDeviceClient/main.py | grep -v grep | awk '{print $4}'`
        if [ -z $status ]
        then
            writelog "重启主程序"
            python /opt/TCPDeviceClient/main.py
            sleep 30
        fi
        status=`ps | grep python | grep /opt/TCPDeviceClient/main.py | grep -v grep | awk '{print $4}'`
        if [ $status = "Z" ]
        then
            writelog "主程序成为僵尸进程，重启系统"
            reboot -f
        fi
        pc=0
    else
        if [ $pc -gt 4 -a $pc -le 9 ];then
            pid=`ps | grep python | grep /opt/TCPDeviceClient/main.py | grep -v grep | awk '{print $1}'`
            if test $pid
            then
                writelog "ping的次数超过5次不通，杀死主程序进程"
                kill -9 $pid
            fi
        elif [ $pc -gt 9 ];then
            writelog "ping的次数超过10次不通，重启系统"
            reboot -f
        fi
        pc=`expr $pc + 1`
    fi
    sleep 1
done
