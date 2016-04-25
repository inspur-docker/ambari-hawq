FROM incloud/ambari-hawq

#----------install chinese support ---
RUN yum -y groupinstall chinese-support
COPY i18n /etc/sysconfig/


#clean yum cache
RUN yum clean all

WORKDIR /