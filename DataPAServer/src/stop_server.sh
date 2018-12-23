#!/usr/bin/env bash

pid=`ps -eaf | grep server-pa | grep -v grep | awk '{print $2}' `

echo $pid
kill -9 $pid

