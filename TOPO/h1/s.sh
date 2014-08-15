#!/bin/bash
if [  -n "$1" ] ;then
    echo $1
else
    echo "hehe"
fi

a=`ifconfig -a | egrep "^*eth0"`
echo $a
#echo $1
