#!/usr/bin/env bash
pwd=$(cd `dirname $0`;pwd)

echo $pwd
source ~/.bashrc
export PYTHONPATH=$pwd/../../
export LANG="zh_CN.UTF-8"
export PYTHONIOENCODING=utf8

cd $pwd
python tibet-kline-make-new.py whenDayClose  --host mongodb --port 27017

# under scott 
# crontab -e 
# * * * /home/scott/Desktop/tibet2/DataPAServer/src/keep_dayclose.sh
# remember to chmod +x keep_dayclose.sh

