#!/usr/bin/env bash

pid=`ps -eaf | grep server-ctp-mark | grep -v grep | awk '{print $2}' `

echo pid