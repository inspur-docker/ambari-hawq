#1.删除hdp.repo和hdp-util.repo
cd /etc/yum.repos.d/
#rm -rf hdp*
#rm -rf HDP*
#rm -rf ambari*
#2.删除安装包
#用yum list installed | grep HDP来检查安装的ambari的包
yum remove -y ambari-agent                                                       
yum remove -y ambari-metrics-hadoop-sink                                         
yum remove -y ambari-metrics-monitor
yum remove -y ambari-metrics-collector                     
yum remove -y atlas-metadata_2_3_0_0_2557-hive-plugin    
yum remove -y bigtop-jsvc                                                        
yum remove -y bigtop-tomcat                              
yum remove -y hadoop_2_3_0_0_2557-client                                         
yum remove -y hadoop_2_3_0_0_2557-conf-pseudo                                    
yum remove -y hadoop_2_3_0_0_2557-doc                                            
yum remove -y hadoop_2_3_0_0_2557-hdfs                                           
yum remove -y hadoop_2_3_0_0_2557-hdfs-datanode                                  
yum remove -y hadoop_2_3_0_0_2557-hdfs-fuse                                      
yum remove -y hadoop_2_3_0_0_2557-hdfs-journalnode                               
yum remove -y hadoop_2_3_0_0_2557-hdfs-namenode                                  
yum remove -y hadoop_2_3_0_0_2557-hdfs-secondarynamenode                         
yum remove -y hadoop_2_3_0_0_2557-hdfs-zkfc                                      
yum remove -y hadoop_2_3_0_0_2557-httpfs                                         
yum remove -y hadoop_2_3_0_0_2557-httpfs-server                                  
yum remove -y hadoop_2_3_0_0_2557-libhdfs                                        
yum remove -y hadoop_2_3_0_0_2557-mapreduce                                      
yum remove -y hadoop_2_3_0_0_2557-mapreduce-historyserver                        
yum remove -y hadoop_2_3_0_0_2557-source                                         
yum remove -y hadoop_2_3_0_0_2557-yarn                                           
yum remove -y hadoop_2_3_0_0_2557-yarn-nodemanager                               
yum remove -y hadoop_2_3_0_0_2557-yarn-proxyserver                               
yum remove -y hadoop_2_3_0_0_2557-yarn-resourcemanager                           
yum remove -y hadoop_2_3_0_0_2557-yarn-timelineserver                            
yum remove -y hdp-select                                 
yum remove -y zookeeper_2_3_0_0_2557           
yum remove -y ranger_2_3_0_0_2557-hdfs-plugin
yum remove -y ranger_2_3_0_0_2557-yarn-plugin
yum remove -y ranger_2_3_0_0_2557-hbase-plugin
yum remove -y hbase_2_3_0_0_2557-doc
yum remove -y falcon_2_3_0_0_2557-doc
yum remove -y accumulo_2_3_0_0_2557-source                              
yum remove -y accumulo_2_3_0_0_2557-test
yum remove -y storm_2_3_0_0_2557-slider-client
yum remove -y slider_2_3_0_0_2557
yum remove -y ranger_2_3_0_0_2557-hive-plugin                           
yum remove -y ranger_2_3_0_0_2557-kafka-plugin                          
yum remove -y ranger_2_3_0_0_2557-knox-plugin                           
yum remove -y ranger_2_3_0_0_2557-storm-plugin
yum remove -y  sqoop.noarch  
yum remove -y  lzo-devel.x86_64  
yum remove -y  hadoop-libhdfs.x86_64  
yum remove -y  rrdtool.x86_64  
yum remove -y  hbase.noarch  
yum remove -y  pig.noarch  
yum remove -y  lzo.x86_64  
yum remove -y  ambari-log4j.noarch  
yum remove -y  oozie.noarch  
yum remove -y  oozie-client.noarch  
yum remove -y  gweb.noarch  
yum remove -y  snappy-devel.x86_64  
yum remove -y  hcatalog.noarch  
yum remove -y  python-rrdtool.x86_64  
yum remove -y  nagios.x86_64  
yum remove -y  webhcat-tar-pig.noarch  
yum remove -y  snappy.x86_64  
yum remove -y  libconfuse.x86_64    
yum remove -y  webhcat-tar-hive.noarch  
yum remove -y  ganglia-gmetad.x86_64  
yum remove -y  extjs.noarch  
yum remove -y  hive.noarch  
yum remove -y  hadoop-lzo.x86_64  
yum remove -y  hadoop-lzo-native.x86_64  
yum remove -y  hadoop-native.x86_64  
yum remove -y  hadoop-pipes.x86_64  
yum remove -y  nagios-plugins.x86_64  
yum remove -y  hadoop.x86_64  
yum remove -y  zookeeper.noarch      
yum remove -y  hadoop-sbin.x86_64  
yum remove -y  ganglia-gmond.x86_64  
yum remove -y  libganglia.x86_64  
yum remove -y  perl-rrdtool.x86_64
yum remove -y  epel-release.noarch
yum remove -y  compat-readline5*
yum remove -y  fping.x86_64
yum remove -y  perl-Crypt-DES.x86_64
yum remove -y  exim.x86_64
yum remove -y ganglia-web.noarch
yum remove -y perl-Digest-HMAC.noarch
yum remove -y perl-Digest-SHA1.x86_64
yum -y remove falcon*
yum -y remove hadoop*       
yum -y remove hbase*           
yum -y remove hive*        
yum -y remove ranger*   
yum -y remove slider*              
yum -y remove storm*
yum -y remove zookeeper* 
yum -y remove ranger*
#3.删除快捷方式
cd /etc/alternatives
rm -rf hadoop-etc 
rm -rf zookeeper-conf 
rm -rf hbase-conf 
rm -rf hadoop-log 
rm -rf hadoop-lib 
rm -rf hadoop-default 
rm -rf oozie-conf 
rm -rf hcatalog-conf 
rm -rf hive-conf 
rm -rf hadoop-man 
rm -rf sqoop-conf 
rm -rf hadoop-conf
#4.删除用户
userdel nagios 
userdel hive 
userdel ambari-qa 
userdel hbase 
userdel oozie 
userdel hcat 
userdel mapred 
userdel hdfs 
userdel rrdcached 
userdel zookeeper 
#userdel mysql 
userdel sqoop
userdel puppet
#5.删除文件夹
rm -rf /usr/hdp
rm -rf /hadoop
rm -rf /etc/hadoop 
rm -rf /etc/hbase 
rm -rf /etc/hcatalog 
rm -rf /etc/hive 
rm -rf /etc/ganglia 
rm -rf /etc/nagios 
rm -rf /etc/oozie 
rm -rf /etc/sqoop 
rm -rf /etc/zookeeper 
rm -rf /var/run/hadoop 
rm -rf /var/run/hbase 
rm -rf /var/run/hive 
rm -rf /var/run/ganglia 
rm -rf /var/run/nagios 
rm -rf /var/run/oozie
rm -rf /var/run/zookeeper
rm -rf /var/log/hadoop 
rm -rf /var/log/hbase 
rm -rf /var/log/hive 
rm -rf /var/log/nagios 
rm -rf /var/log/oozie 
rm -rf /var/log/zookeeper 
rm -rf /usr/lib/hadoop
rm -rf /usr/lib/hbase 
rm -rf /usr/lib/hcatalog 
rm -rf /usr/lib/hive 
rm -rf /usr/lib/oozie 
rm -rf /usr/lib/sqoop 
rm -rf /usr/lib/zookeeper 
rm -rf /var/lib/hive 
rm -rf /var/lib/ganglia 
rm -rf /var/lib/oozie 
rm -rf /var/lib/zookeeper 
rm -rf /var/tmp/oozie 
rm -rf /tmp/hive 
rm -rf /tmp/nagios 
rm -rf /tmp/ambari-qa 
rm -rf /tmp/sqoop-ambari-qa 
rm -rf /var/nagios 
rm -rf /hadoop/oozie 
rm -rf /hadoop/zookeeper 
rm -rf /hadoop/mapred 
rm -rf /hadoop/hdfs 
rm -rf /tmp/hadoop-hive 
rm -rf /tmp/hadoop-nagios 
rm -rf /tmp/hadoop-hcat 
rm -rf /tmp/hadoop-ambari-qa 
rm -rf /tmp/hsperfdata_hbase 
rm -rf /tmp/hsperfdata_hive 
rm -rf /tmp/hsperfdata_nagios 
rm -rf /tmp/hsperfdata_oozie 
rm -rf /tmp/hsperfdata_zookeeper 
rm -rf /tmp/hsperfdata_mapred 
rm -rf /tmp/hsperfdata_hdfs 
rm -rf /tmp/hsperfdata_hcat 
rm -rf /tmp/hsperfdata_ambari-qa
rm -rf /var/run/ambari-metrics-monitor
rm -rf /var/run/hadoop-*
rm -rf /var/log/hadoop-*
rm -rf /etc/accumulo/2.3.0.0-2557/
rm -rf /etc/accumulo/conf.install/
rm -rf /usr/lib/ambari-*
rm -rf /var/log/atlas
rm -rf /var/log/falcon
rm -rf /var/log/flume
rm -rf /var/log/hive-hcatalog
rm -rf /var/log/kafka
rm -rf /var/log/ntpstats
rm -rf /var/log/solr
rm -rf /var/log/spark
rm -rf /var/log/storm
rm -rf /var/log/webhcat
rm -rf /var/log/hue
#5.重置数据库，删除ambari包 #采用这句命令来检查yum list installed | grep ambari 
ambari-agent stop 
yum remove -y ambari-* 
yum remove -y postgresql 
rm -rf /var/lib/ambari* 
rm -rf /var/log/ambari* 
rm -rf /etc/ambari*
