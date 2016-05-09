#!/bin/bash

#Path to install HUE to e.g. /usr/local/hue
HUE_PATH=$1

#hue user e.g. hue
HUE_USER=$2


    echo "Starting Hue install"
    
	getent passwd $HUE_USER
	if [ $? -eq 0 ]; then
    	echo "the user exists, no need to create"
	else
    
	    echo "creating hue user"
	    adduser $HUE_USER
	fi


	hadoop fs -test -d /user/$HUE_USER
	if [ $? -eq 1 ]; then
    	echo "Creating user dir in HDFS"
    	sudo -u hdfs hdfs dfs -mkdir -p /user/$HUE_USER
    	#sudo -u hdfs hdfs dfs -mkdir -p /user/oozie/share/lib/livy
    	sudo -u hdfs hdfs dfs -chown $HUE_USER /user/hue 
	fi
	

