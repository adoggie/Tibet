#!/usr/bin/env bash


crontab -e

add following script lines.

55 8 * * * /home/scott/Desktop/Projects/Tibet/DataPAServer/src/start_server.sh
45 11 * * * /home/scott/Desktop/Projects/Tibet/DataPAServer/src/stop_server.sh

0 13 * * * /home/scott/Desktop/Projects/Tibet/DataPAServer/src/start_server.sh
50 15 * * * /home/scott/Desktop/Projects/Tibet/DataPAServer/src/stop_server.sh

55 20 * * * /home/scott/Desktop/Projects/Tibet/DataPAServer/src/start_server.sh
45 2 * * * /home/scott/Desktop/Projects/Tibet/DataPAServer/src/stop_server.sh


50 15 * * * /home/scott/Desktop/Projects/Tibet/DataPAServer/src/keep_dayclose.sh
45 2 * * * /home/scott/Desktop/Projects/Tibet/DataPAServer/src/keep_nightcose.sh

