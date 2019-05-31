
GeniusBarMaker
-------
Ctp 行情k线计算服务

1. main.py   k线计算主程序。 等待行情推送tick到redis的publish通道 `ctp.tick.pub`。
读取tick 缓存并计算出 1,5,15,30,60分钟的周期k线，并发送到redis的publish
通道`ctp.bar.pub`,待 `CtpMarketRecorder`读取并持久化k线到mongodb。

2. playTick.py  当main.py并不能接收全部的开盘tick时，需要在盘后重新生成当日所有k线记录，这就需要
`playTick.py`读取当日的tick，并再次发送给 `main.py`进行处理。 

## 配置

`config.REAL` 盘中运行时需打开 REAL ，将定时产生分钟`break`信号，触发前一个k线周期结束

