#!/usr/bin/env python
from resource_management import *
import os

# config object that holds the configurations declared in the -config.xml file
config = Script.get_config()


#e.g. /var/lib/ambari-agent/cache/stacks/HDP/2.3/services/HUE/package
service_packagedir = os.path.realpath(__file__).split('/scripts')[0]
cluster_name=str(config['clusterName'])



#####################################
#Hue configs
#####################################

hue_install_dir = '/usr/local'
hue_dir = hue_install_dir + '/hue'
hue_conf= hue_dir + '/desktop/conf'
hue_bindir = hue_dir + '/build/env/bin' 
hue_eachconf= hue_conf + '/eachconf' 


#server_dir=os.path.join(*[hue_install_dir,'hue','server'])  

hue_user = config['configurations']['hue-env']['hue.user']
hue_group = config['configurations']['hue-env']['hue.group'] 
hue_log_dir = config['configurations']['hue-env']['hue.log.dir'] 
hue_log = hue_log_dir+'/hue-install.log' 

hue_piddir = config['configurations']['hue-env']['hue_pid_dir']
hue_port = config['configurations']['hue-env']['hue.port']
hue_pidfile = format("{hue_piddir}/hue-{hue_port}.pid")

hue_log_content = config['configurations']['hue-log4j-env']['content']

#hue.ini
#hue_conf_content = config['configurations']['hue-config']['content']
hue_desktop_content = config['configurations']['hue-Desktop']['content']
hue_notebook_content = config['configurations']['hue-Notebook']['content']
hue_hadoop_content = config['configurations']['hue-Hadoop']['content']
hue_hive_content = config['configurations']['hue-Hive']['content']
hue_spark_content = config['configurations']['hue-Spark']['content']
hue_oozie_content = config['configurations']['hue-Oozie']['content']
hue_pig_content = config['configurations']['hue-Pig']['content']
hue_hbase_content = config['configurations']['hue-Hbase']['content']
hue_solr_content = config['configurations']['hue-Solr']['content']
hue_zookeeper_content = config['configurations']['hue-Zookeeper']['content']
hue_rdbms_content = config['configurations']['hue-RDBMS']['content']
