# _*_ coding: UTF-8 _*_
'''
Created on 2015/3/20

@author: oscal
'''

Err_Unknow = -1
Err_Success = 0
Err_Dev_Offline = 1
Err_Dev_Did_Binding = 2
err_exception = 40000
Err_Params = 40010
Err_Dev_Ctrl_Fail = 40020
Err_DB_Write_Fail = 40030
Err_Data_Search_Fail = 40040

Err_Params_Format = 40011
Err_Params_Value = 40012

Err_Dev_Unlocking = 40021
Err_Dev_Commond_Timeout = 40022

Err_DB_Delete_Fail = 40031
Err_DB_Update_Fail = 40032
Err_Data_Notexist_Fail = 40041
Err_File_Notexist_Fail = 40042


ERR_TEXTS = {
             Err_Unknow:u'未知错误',
             Err_Success:u'成功',
             Err_Dev_Offline:u'设备未上线',
             Err_Dev_Did_Binding:u'该设备已绑定给其它经销商',
             err_exception:u'异常',
             Err_Params:u'请求参数错误',
             Err_Dev_Ctrl_Fail:u'设备控制命令执行失败',
             Err_DB_Write_Fail:u'写数据到数据库失败',
             Err_Data_Search_Fail:u'查询数据失败',
             Err_Params_Format:u'请求参数格式错误',
             Err_Params_Value:u'请求参数值错误',
             Err_Dev_Unlocking:u'设备正在执行开锁命令',
             Err_Dev_Commond_Timeout:u'设备控制命令执行超时',
             Err_DB_Delete_Fail:u'删除数据失败',
             Err_DB_Update_Fail:u'更新数据失败',
             Err_Data_Notexist_Fail:u'符合条件的数据不存在',
             Err_File_Notexist_Fail:u'文件不存在',
             }
    
    
    
    
    