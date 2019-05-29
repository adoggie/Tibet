

xtpMonitor 
------
中泰 XTP 程序化日志接入服务

    @brief:  xtp monitor python接口封装
    @author: scott  24509826@qq.com
    @date: 2018/7/18

使用指引：
 1. windows 主机上启动 xtp-monitor-client
 2. linux 主机运行  xtp-monitor
    client 端输入用户名和密码，会通过xhost转到 xtp-monitor 的登录函数入口进行校验，返回0表示身份合法。
       注意： password 是两端进行md5计算生成
    xpt-monitor 从 系统的消息队列中读取系统日志信息，并中转到前端的 monitor-client .
    反正根据xtp的要求必须这么操作才能保证环境内的运行数据被传递到xtp环境外部。
