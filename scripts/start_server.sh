#!/usr/bin/env bash



pwd=$(cd `dirname $0`;pwd)

bash $pwd/stop_server.sh

cd $pwd/market
chmod +x CtpMarketCxx
nohup ./CtpMarketCxx &

cd $pwd/trader
echo `pwd`
chmod +x CtpTradeCxx
nohup ./CtpTradeCxx &



echo $pwd

source ~/.bashrc
export PYTHONPATH=$pwd/pythonpath
export LANG="zh_CN.UTF-8"
export PYTHONIOENCODING=utf8

cd $pwd/geniusbar
nohup python geniusbarmaker.py &

cd $pwd/datarecorder/src
nohup python server-data-resource.py &





