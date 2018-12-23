#!/usr/bin/env bash

pwd=$(cd `dirname $0`;pwd)

echo $pwd
source ~/.bashrc
export PYTHONPATH=$pwd/../../
cd $pwd
python tibet-kline-make.py whenNightClose  --host 192.168.99.22 --port 27018

# under scott
# crontab -e
# * * * /home/scott/Desktop/tibet2/DataPAServer/src/keep_dayclose.sh
# remember to chmod +x keep_dayclose.sh


# --- .bashrc  确保一下内容出现----
# .bashrc

# Source global definitions
#if [ -f /etc/bashrc ]; then
#	. /etc/bashrc
#fi
#export PATH="/home/scott/anaconda2/bin:$PATH"