

1. 每日交易之前 运行初始化 init_accounts.py , init_codes.py 来配置当日交易的运行参数


问题记录
=======
2019.5.24
  1. 程序在9：30之前启动，在9：14分进行下单交易，并将交易状态改变成 open ，导致开盘时间段无法进行正常的open操作
     解决：
       策略触发时 检查是否在开盘时间 >=  9:30  (sg.fisher.stutils.Stocks.in_trading_time() )
