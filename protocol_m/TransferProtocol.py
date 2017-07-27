# _*_ coding: UTF-8 _*_
'''
Created on 2015/03/01

@author: oscal
'''
import ctypes as ct
from StructBase import LittleEndianStructBase

SHAKE_HAND_INTERVAL = 11  # 10s


class MsgHead(LittleEndianStructBase):
    _fields_ = [
        ('iMsgType', ct.c_int32),
        ('iSubMsgType', ct.c_int32),
        ('iPayloadLen', ct.c_int32),
        ('iCheckSum', ct.c_int32),
        ('iFeedBack', ct.c_int32)
    ]

    def pack(self):
        self.iCheckSum = (self.iMsgType + self.iSubMsgType + self.iPayloadLen + self.iFeedBack) & 0xffffffff
        return LittleEndianStructBase.pack(self)

    def testCheckSum(self):
        return self.iCheckSum == (self.iMsgType + self.iSubMsgType + self.iPayloadLen + self.iFeedBack) & 0xffffffff


class MsgTypeEnum:
    SHAKE_HAND = 0x00010000  # 握手
    DEVICE_CONTROL = 0x00010003  # 设备控制
    STATUS_REPORT = 0x00020001  # 状态上报
    LOG_REPORT = 0x00020002  # 日志上报
    ALARM_REPORT = 0x00020003  # 报警信息上报
    LOGIN_AUTH = 0x00030000  # 登录授权请求
    SOFTWARE_UPGRADE = 0x00070000  # 设备软件升级
    ALIVE = 0x01000010  # 在线查询
    SHIPMENT = 0x01000020  # 出货命令
    TEMPERATURE_MODE = 0x01000040  # 设置售卖机温控模式
    TEMPERATURE_RANGE = 0x01000080  # 设置售卖机温度范围
    SHIPMENT_SOUND = 0x01000100  # 播放声音
    TEMPERATURE_RANGE_REPORT = 0x01000200  # 温度范围上报
    SHIPMENT_MENCI_REPORT = 0x01000400  # 出货口门磁状态上报
    TEMPERATURE_ADJUSTMODE = 0x01000800  # 设置温度示数 0减---- 1加
    TEMPERATURE_ADJUSTVALUE = 0x01001000  # 调整值
    QRCODE_REPORT = 0x01004000  # 二维码数据上报
    QRCODE_LED_SET = 0x01008000  # 二维码LED控制

    CTL_MSG_REP = 0x01000002  # 消息回复


class MsgSubTypeEnum:
    UNUSED = 0x00000000  # 消息子类型无效
    REQUEST = 0x00010000  # 设备端发起的请求
    RESPONSE = 0x00020000  # 控制中心返回的响应
    COMMAND = 0x00030000  # 控制中心发起的命令
    RESULT = 0x00040000  # 设备返回的结果


class LoginAuth(LittleEndianStructBase):
    _fields_ = [
        ('cDeviceID', ct.c_char * 20),
        ('cVersion', ct.c_char * 12),
        ('cDeviceIP', ct.c_char * 20),
        ('iListenPort', ct.c_int32)
    ]


class LoginResultEnum:
    LOGIN_PASS = 0  # 允许登录
    LOGIN_REFUSED = 1  # 拒绝登录
    ERROR_VERSION = 2  # 协议版本号错误


class Result(LittleEndianStructBase):
    _fields_ = [
        ('iResult', ct.c_int32)
    ]


class ControllerStatus(LittleEndianStructBase):
    inDoorStatus = 0  # 门磁状态
    inVibrationStatus = 1  # 振动状态
    inPirStatus = 2  # 热释电状态

    outLockStatus = 0  # 门锁状态
    outSoundLightStatus = 1  # 声光报警状态

    _fields_ = [
        ('iInputStatus', ct.c_int32 * 4),
        ('iOutputStatus', ct.c_int32 * 4)
    ]


# enum SHIPMENT_SUB_TYPE
class ShipmentTypeEnum:
    SHIPMENT_IN = 0
    SHIPMENT_OUT = 1


class ShipmentStruct(LittleEndianStructBase):
    _fields_ = [
        ('uiShipmentType', ct.c_uint32),
        ('uiShipmentID', ct.c_uint32),
        ('uiX', ct.c_uint32),
        ('uiY', ct.c_uint32),
        ('uiZ', ct.c_uint32),
        ('uiResult', ct.c_uint32)
    ]


class ShakeHandStruct(LittleEndianStructBase):
    _fields_ = [
        ('uiMode', ct.c_uint8),
        ('uiStatus', ct.c_uint8),
        ('uiTemperature', ct.c_int16)
    ]


class TemperatureModeEnum:
    TEMPERATURE_MODE_COLD = 0
    TEMPERATURE_MODE_HOT = 1


class TemperatureModeStruct(LittleEndianStructBase):
    _fields_ = [
        ('uiMode', ct.c_uint32)
    ]


class TemperatureRangeStruct(LittleEndianStructBase):
    _fields_ = [
        ('iUpLimit', ct.c_int32),
        ('iDownLimit', ct.c_int32),
    ]


class ShipmenSoundStruct(LittleEndianStructBase):
    _fields_ = [
        ('uiSound', ct.c_uint32)
    ]


class ShipmenSoundEnum:
    SHIPMENT_SOUND_CLOSE = 0
    SHIPMENT_SOUND_OK = 1
    SHIPMENT_SOUND_FAIL = 2
    SHIPMENT_SOUND_NOTFULL = 3
    QRCODE_SOUND_SCAN = 4  # 请扫描
    QRCODE_SOUND_DONE = 5  # 已完成


class LogStruct(LittleEndianStructBase):
    _fields_ = [
        ('uiLogID', ct.c_uint32),
        ('usLogType', ct.c_uint16),
        ('usLevel', ct.c_uint16),
        ('i64Ts', ct.c_int64),
        ('cContext', ct.c_char * 200)
    ]


# enum LOG_TYPE_E
class LogTypeEnum:
    FD_LOG = 0  # 指纹仪管理日志
    OP_LOG = 1  # 操作日志
    AL_LOG = 2  # 报警日志


# enum LOG_SUB_TYPE_E
class LogSubTypeEnum:
    LOG_OP_SETING = 0  # 设置日志
    LOG_OP_OPENDOOR = 1  # 开门日志（门磁）,正常开门
    LOG_OP_CLOSEDOOR = 2  # 关门日志（门磁）

    LOG_OP_SYSTEMSTART = 14  # 程序启动日志
    LOG_OP_SYSTEMEND = 15  # 程序结束

    LOG_ALARM_SHAKING = 17  # 震动报警日志

    LOG_ALARM_UNLAWOPEN = 23  # 非法开门日志*/
    LOG_ALARM_OPENLONGTIME = 24  # 主控锁打开时间过久日志*/

    LOG_OP_UNLOCK = 32  # 开锁操作日志（电子锁）
    LOG_OP_SHIPMENT = 33  # 接收到出货指令日志
    LOG_OP_SHIPMENT_OVER = 34  # 出货结束日志
    LOG_OP_UPDATE = 35  # 升级日志，升级完成后记录下升级的版本号


class AlarmStruct(LittleEndianStructBase):
    _fields_ = [
        ('cType', ct.c_byte),
        ('cSubType', ct.c_byte),
        ('cAction', ct.c_byte),
        ('cLevel', ct.c_byte),
        ('iValue', ct.c_int32),
        ('bVideo', ct.c_int32),
        ('byVideoChannel', ct.c_byte * 4),
        ('uiTime', ct.c_uint32)
    ]


# enum ALAM_ACTION_E
class AlamActionEnum:
    AL_START_ACTION = 0  # 开始
    AL_OVER_ACTION = 1  # 结束
    AL_UNKNOWN_ACTION = 2  # 第三态


class AlarmLevelEnum:
    ALARM_ONELEVEL = 1  # 一级
    ALARM_TWOLEVEL = 2  # 二级
    ALARM_THRLEVEL = 3  # 三级


class AlarmTypeEnum:
    ALARM_PHYSICAL = 0  # 物理报警
    ALARM_LOGIC = 1  # 逻辑报警
    ALARM_FAULT = 2  # 故障报警
    ALARM_REMIND = 3 #提示


class AlarmPhysicalSubTypeEnum:
    ALARM_SHAKING = 1  # 震动报警


class AlarmLogicalSubTypeEnum:
    ALARM_TEMPERATURE = 0  # 温度报警
    ALARM_UNLAWOPEN = 2  # 非法开门
    ALARM_OPENLONGTIME = 3  # 主控锁打开时间过久
    ALARM_VIDEOTAPE = 4 #录像


class AlarmFaultSubTypeEnum:
    ALARM_TEMPERATURE_SHUTDOWN = 4  # 温控停机报警


class UpgradeFile(LittleEndianStructBase):
    _fields_ = [
        ('cFileName', ct.c_char * 256),
        ('iFileSize', ct.c_int32),
        ('uiCRC32', ct.c_uint32)
    ]


class UpgradeResultEnum:
    FILE_ERROR = 0  # 文件不完整
    FILE_DECRYPT_FAIL = 1  # 文件解密失败
    FILE_UNCOMPRESS_FAIL = 2  # 文件解压失败
    LATEST_VERSION = 3  # 已是最新版本
    COMPLETED = 4  # 升级完毕


# enum DEVICE_CONTROL_TYPE_E
class DeviceControlTypeEnum:
    REMOTE_OPENDOOR_COMMAND = 0x00010001  # 远程开柜命令
    REMOTE_SETLED_COMMAND = 0x00010003  # 远程设置LED命令


class RemoteOpenDoorParam(LittleEndianStructBase):
    _fields_ = [
        ('iIndex', ct.c_int32)
    ]


class LEDInfoStruct(LittleEndianStructBase):
    _fields_ = [
        ('length', ct.c_int32),
        ('mode', ct.c_int32),
        ('speed', ct.c_int32),
        ('info', ct.c_char * 400)
    ]


# enum SH_MENCI_ST_E
class ShipmentMenciStatusEnum:
    SH_MENCI_ST_CLOSE = 0
    SH_MENCI_ST_OPEN = 1


class ShipmentMenciStruct(LittleEndianStructBase):
    _fields_ = [
        ('uiMenciSt', ct.c_uint32)  # 售卖机出货口门磁状态
    ]


# 设置温度调节值
class TemAdjustValueStruct(LittleEndianStructBase):
    _fields_ = [
        ('uiMode', ct.c_uint32),  # 0减 1加
        ('uiValue', ct.c_uint32)  # 值
    ]


# 温度板停机上报
class TemShutdownStruct(LittleEndianStructBase):
    _fields_ = [
        ('utime', ct.c_uint32)  # 停机时间戳
    ]


# 二维码扫描信息上报
class QRCodeStruct(LittleEndianStructBase):
    _fields_ = [
        ('time', ct.c_uint32),  # 扫码时间戳
        ('len', ct.c_uint32),  # 扫描信息实际长度
        ('qrcode', ct.c_char * 1024)  # 扫描信息
    ]


# 二维码扫码灯控制
class QRCodeLEDStruct(LittleEndianStructBase):
    _fields_ = [
        ('uState', ct.c_uint32)  # 0-->关闭LED   1-->打开LED
    ]
