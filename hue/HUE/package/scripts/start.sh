#!/bin/bash
set -e

#Path to start.jar e.g. /usr/local/hue
HUE_PATH=$1

#Logfile e.g. /var/log/hue.log
LOGFILE=$2

#pid file e.g. /var/run/hue.pid
PID_FILE=$3

#path containing start.jar file e.g. /usr/local/hue
START_PATH=$4
 
PID_DIR=$(dirname "$PID_FILE")

#Create pid dir if it does not exist
if [ ! -d "$PID_DIR" ]
then
	echo "Creating PID_DIR: $PID_DIR"
	mkdir -p $PID_DIR
fi

#start Hue if not already started from $START_PATH dir
if [ ! -f "$PID_FILE" ]
then
	cd $START_PATH
	echo "Starting Hue..."	
	./hue runcpserver >> $LOGFILE 2>&1 &	
	echo $! > $PID_FILE
fi
