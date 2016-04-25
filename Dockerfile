FROM incloud/ambari-agent

#-------------local hawq rpm repo
ADD PIVOTAL-HDB /opt/PIVOTAL-HDB/
#
RUN cd /opt/PIVOTAL-HDB/ && cat hawq-2.0.0.0_beta-21030.x86_64.rpm.a* > hawq-2.0.0.0_beta-21030.x86_64.rpm && rm -f hawq-2.0.0.0_beta-21030.x86_64.rpm.a*
COPY PIVOTAL-HDB/*.repo /etc/yum.repos.d/

#-------------install hadoop_2.3 && hawq && depends
COPY repo-local/* /etc/yum.repos.d/
#COPY repo-origin/* /etc/yum.repos.d/
RUN yum -y install unzip hdp-select rpcbind 'hadoop_2_3_*' snappy snappy-devel ntp hawq

#-----------install ambari-server (all in one)
RUN yum -y install ambari-server
#-----------Bug fixes : rename hawq services script "constants.py -> hawqconstants.py"
COPY hawq/ambari/common-services/HAWQ/2.0.0/package/scripts/* /var/lib/ambari-server/resources/common-services/HAWQ/2.0.0/package/scripts/

#------------install hawq service to HDP stack
COPY hawq/ambari/services/HAWQ/* /var/lib/ambari-server/resources/stacks/HDP/2.3/services/HAWQ/
COPY hawq/ambari/services/PXF/* /var/lib/ambari-server/resources/stacks/HDP/2.3/services/PXF/

#------------local HDP stack repo
COPY hawq/ambari/repoinfo.xml /var/lib/ambari-server/resources/stacks/HDP/2.3/repos/

#clean yum cache
RUN yum clean all

WORKDIR /