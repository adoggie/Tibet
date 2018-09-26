
服务说明
-----

1. CtpMarket
   port:18801 
   
2. CtpTrade
   port: 0 
   
3. DataPAServer
   port: 18802
   
4. DataResServer
   port: 18803
    
5. StrategyRunner 策略运行器

  http: <host>:18804/path
     path: 
       - console/  
       - console/orders 下单
       - api/orders  
           POST   下单
           DELETE 撤单
        
6. XtpMarket
    port: 18804