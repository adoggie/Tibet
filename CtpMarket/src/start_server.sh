#!/usr/bin/env bash
pwd=$(cd `dirname $0`;pwd)

echo $pwd
source ~/.bashrc
export PYTHONPATH=$pwd/../../
export LANG="zh_CN.UTF-8"
export PYTHONIOENCODING=utf8
cd $pwd
python server-ctp-market.py




