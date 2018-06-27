
ctpTrade 
------
ctp期货交易适配器

## 运行

Trade程序由外部加载器启动运行。加载器传入参数  `--product`,`--account` 参数用于标识当前Trade适配器打开的对应资金账户。 

```
    python server-ctp-trade.py --product=future --acount=htqz-01
    python server-ctp-trade.py --product=future --acount=htqh-02 --mode=dev 
    
``` 


* Http 接口


