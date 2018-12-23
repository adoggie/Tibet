#!/usr/bin/env bash
pwd=$(cd `dirname $0`;pwd)

echo $pwd
source ~/.bashrc
export PYTHONPATH=$pwd/../../
export LANG="zh_CN.UTF-8"
export PYTHONIOENCODING=utf8
cd $pwd
#python tibet-kline-make.py whenNightClose  --host 192.168.99.22 --port 27018
python tibet-kline-make-new.py whenNightClose  --host mongodb --port 27017
# under scott 
# crontab -e 
# * * * /home/scott/Desktop/tibet2/DataPAServer/src/keep_dayclose.sh
# remember to chmod +x keep_dayclose.sh

