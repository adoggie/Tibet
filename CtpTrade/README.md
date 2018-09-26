
ctpTrade 
------
ctp期货交易适配器

## 运行

Trade程序由外部加载器启动运行。
加载器传入参数 
* `--product` 期货、股票等等
* `--account` 标识当前Trade适配器对应资金账户 

<pre>
    python server-ctp-trade.py --product=future --account=htqz-01
    python server-ctp-trade.py --product=future --account=htqh-02 --mode=dev 
    
</pre>

多实例运行
-----

通过启动脚本start-server.sh 来启动多交易实例的运行。

配置
------
开发、生产环境中的账号信息时写入redis配置项中
<pre>
[ mantis.trade.constants ]
DevelopAccountNameFormat    = "development.accounts.{product}.{account}"
TradeAccountNameFormat      = "trade.accounts.{product}.{account}"
</pre>

创建账号的脚本在：
> StrategeRunner/tests/
*   settings.yaml   
*   test-config-init-data.py 



设计
-----
交易操作包括发单、撤单、回报等均写入 mongodb.

* DB: TradeLog_Ctp_{account}  数据库
* Coll: 
    1. send_order   - 发单记录
    2. cancel_order -  撤单记录
    3. event_order  - 回单记录
    4. event_trade  - 成交记录 
    

