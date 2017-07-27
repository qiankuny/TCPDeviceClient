#!/bin/sh

sleep 60
pc=0
while :
do
    ra=`ifconfig | grep ra0 | grep -v grep | awk '{print $1}'`
    if [ -z $ra ]
    then
        pid=`ps | grep wpa_supplicant | grep 'wpa_supplicant -B -Dwext -ira0 -c /etc/wpa_supplican' | grep -v grep | awk '{print $1}'`
        if test $pid
        then
            kill -9 $pid
        fi
        pid=`ps | grep udhcpc | grep 'udhcpc -i ra0' | grep -v grep | awk '{print $1}'`
        if test $pid
        then
            kill -9 $pid
        fi
        if [ -e /var/run/wpa_supplicant/ra0 ]
        then
            rm /var/run/wpa_supplicant/ra0
        fi
        sleep 10
        ssid=`cat /etc/wpa_supplicant.conf | grep ssid=\" | cut -d "=" -f2`
        while :
        do
            ifconfig ra0 up
            ra=`ifconfig | grep ra0 | grep -v grep | awk '{print $1}'`
            if [ $ra ]
            then
                break
            fi
			sleep 1
        done
        while :
        do
            getwifi=`iwlist ra0 scanning | grep $ssid | grep -v grep`
            if test $getwifi
            then
                break
            fi
            sleep 1
        done
        wpa_supplicant -B -Dwext -ira0 -c /etc/wpa_supplicant.conf -d
        while :
        do
            sleep 1
            pid=`ps | grep wpa_supplicant | grep 'wpa_supplicant -B -Dwext -ira0 -c /etc/wpa_supplican' | grep -v grep | awk '{print $1}'`
            if test $pid
            then
                break
            fi
        done
        udhcpc -i ra0
        while :
        do
            sleep 1
            pid=`ps | grep udhcpc | grep 'udhcpc -i ra0' | grep -v grep | awk '{print $1}'`
            if test $pid
            then
                break
            fi
        done
        pid=`ps | grep python | grep /opt/TCPDeviceClient/main.py | grep -v grep | awk '{print $1}'`
        if test $pid
        then
            kill -9 $pid
        fi
    fi

    ping -c 1 8.8.8.8 > /dev/null 2>&1
    if [ $? -eq 0 ];then
        status=`ps | grep python | grep /opt/TCPDeviceClient/main.py | grep -v grep | awk '{print $4}'`
        if [ -z $status ]
        then
            python /opt/TCPDeviceClient/main.py
            sleep 30
        fi
        status=`ps | grep python | grep /opt/TCPDeviceClient/main.py | grep -v grep | awk '{print $4}'`
        if [ $status = "Z" ]
        then
            reboot -f
        fi
        pc=0
    else
        if [ $pc -gt 1 -a $pc -le 9 ];then
            pid=`ps | grep python | grep /opt/TCPDeviceClient/main.py | grep -v grep | awk '{print $1}'`
            if test $pid
            then
                kill -9 $pid
            fi
        elif [ $pc -gt 9 ];then
            reboot -f
        fi
        pc=`expr $pc + 1`
    fi
    sleep 1
done
