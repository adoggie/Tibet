#coding:utf-8

"""
@brief:  xtp monitor python接口封装
@author: scott  24509826@qq.com
@date: 2018/7/18


@xtpMonitor 使用指引：
 1. windows 主机上启动 xtp-monitor-client
 2. linux 主机运行  xtp-monitor
    client 端输入用户名和密码，会通过xhost转到 xtp-monitor 的登录函数入口进行校验，返回0表示身份合法。
       注意： password 是两端进行md5计算生成
    xpt-monitor 从 系统的消息队列中读取系统日志信息，并中转到前端的 monitor-client .
    反正根据xtp的要求必须这么操作才能保证环境内的运行数据被传递到xtp环境外部。

"""

from ctypes import *
_lib = cdll.LoadLibrary('libxtpmonitorguestapi.so')

XTP_HOST_ERR_MSG_LEN = 124

""""
reference : 
	xtp_monitor_api_struct_common.h
	xtp_monitor_guest_api.h

#define XTP_HOST_ERR_MSG_LEN  124
typedef struct XTPHostErrorInfoStruct
{
	int32_t	error_id;
	char	error_msg[XTP_HOST_ERR_MSG_LEN];
} XTPHRI;
"""

class XTPHostErrorInfoStruct(Structure):
	_pack_ = 8
	_fields_ = [
		('error_id', c_int),
        ('error_msg',c_char *XTP_HOST_ERR_MSG_LEN)
	]
XTPHRI = XTPHostErrorInfoStruct

"""
	typedef int32_t(*MonitorClientLoginFunc)(const char* username, const char* password, const char* mac_add, const char* ip);
	typedef int32_t(*StartFunc)();
	typedef int32_t(*StopFunc)();
"""

MonitorClientLoginFunc = CFUNCTYPE(c_int32,c_char_p, c_char_p, c_char_p,c_char_p)
StartFunc = CFUNCTYPE(c_int32)
StopFunc = CFUNCTYPE(c_int32)

# bool RegisterMonitorClientLoginFunc(MonitorClientLoginFunc func);
RegisterMonitorClientLoginFunc = _lib.RegisterMonitorClientLoginFunc
RegisterMonitorClientLoginFunc.restype = c_bool
RegisterMonitorClientLoginFunc.argtypes = [MonitorClientLoginFunc]


# MONITOR_GUEST_API_EXPORT bool RegisterStartFunc(StartFunc func);
RegisterStartFunc = _lib.RegisterStartFunc
RegisterStartFunc.restype = c_bool
RegisterStartFunc.argtypes = [StartFunc]

# MONITOR_GUEST_API_EXPORT bool RegisterStopFunc(StopFunc func);
RegisterStopFunc = _lib.RegisterStopFunc
RegisterStopFunc.restype = c_bool
RegisterStopFunc.argtypes = [StopFunc]

# MONITOR_GUEST_API_EXPORT int32_t ConnectToMonitor(const char* ip, int port, const char* user, bool strategy_is_start);

ConnectToMonitor = _lib.ConnectToMonitor
ConnectToMonitor.restype = c_int32
ConnectToMonitor.argtypes = [c_char_p,c_int32,c_char_p,c_bool]

# MONITOR_GUEST_API_EXPORT int32_t SendMsg(int level, const char* topic, const char* log_text, int alarm_wav_index = -1);
SendMsg = _lib.SendMsg
SendMsg.restype = c_int32
SendMsg.argtypes = [c_int32,c_char_p,c_char_p,c_int32]

# MONITOR_GUEST_API_EXPORT void GetApiLastError(XTPHRI *error_info);

GetApiLastError = _lib.GetApiLastError
GetApiLastError.restype = None
GetApiLastError.argtypes = [POINTER(XTPHostErrorInfoStruct)]


def onMonitorClientLogin( username, password, mac_addr, ip):
	print 'Xtp Monitor Client Login ..'
	print username, password, mac_addr, ip
	print 'Passed ..'
	return 0


def onStart():
	print 'Remote Command: Start ..'
	return 0


def onStop():
	print 'Remote Command: Stop ..'
	return 0

StartHandler = StartFunc(onStart)
def test_connect():
	import time
	# 注意： 必须保留 StartFunc(onStart) 的函数对象为全局，避免被GC回收导致回调异常

	RegisterStartFunc(StartHandler)
	RegisterStopFunc(StopFunc(onStop))
	RegisterMonitorClientLoginFunc(MonitorClientLoginFunc(onMonitorClientLogin))
	server = '120.27.164.138'
	ip = '120.27.164.138'
	port = 7749
	username = 'test39-guest'

	ret = ConnectToMonitor(ip, port, username, True)
	print 'Connect XtpHost :', ret

	time.sleep(10000)

if __name__ == '__main__':
	test_connect()