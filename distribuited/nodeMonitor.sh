#!/bin/sh

fileName="/opt/nike/nodeStarter.sh"
step=2

rm -rf $fileName

while true; do
    ps -fe|grep 'role node' |grep -v grep
    if [ $? -ne 0 ]; then
        echo "start process....."
        if [ ! -f $fileName ]; then
            echo "Node Start file not exist"
        else
            chmod 777 $fileName
#export DISPLAY=:0
            sh $fileName
        fi
    else
        echo "runing....."
    fi
    sleep $step
done

echo "assume never run to here"
exit 0

