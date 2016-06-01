#!/bin/bash

#add the environment variable to /etc/profile
sed -i '$a## ------------HUE->SPARK_HOME and HADOOP_CONF_DIR--------------------- ##' /etc/profile
sed -i '$aexport SPARK_HOME=/usr/hdp/current/spark-client' /etc/profile
sed -i '$aexport PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin' /etc/profile
sed -i '$aexport HADOOP_CONF_DIR=/usr/hdp/current/hadoop-client/conf' /etc/profile
source /etc/profile
