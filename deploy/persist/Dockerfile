FROM incloud/ambari-hawq:zh_CN

#PXF安装
RUN curl -o /etc/yum.repos.d/CentOS-Base.repo  http://mirrors.aliyun.com/repo/Centos-6.repo && yum clean all
RUN yum -y install pxf-service  apache-tomcat pxf-hdfs pxf-hive install pxf-hbase
#RUN useradd pxf && useradd tomcat
#/etc/pxf/conf/pxf-env.sh
RUN mkdir /usr/java && ln -s /opt/java/jdk1.8.0_60 /usr/java/default

#gpadmin用户，密码gpadmin（需要与hawq安装脚本相同-HAWQ\2.0.0.\package\scripts\common.py的__create_hawq_user()方法）
#RUN userdel -r gpadmin
RUN useradd -p '$6$04ecjJSX$fWelhVL1H1wJB0AR.OCcv.qthmhHVDLYvkZw8qW05kNFaoSFFEMDzjci2gniDN2ndCy3TBqOHoC91vK9eh.S/0' gpadmin && su -c "ssh-keygen -q -f /home/gpadmin/.ssh/id_rsa -N ''" gpadmin && rm -f /home/gpadmin/.ssh/*

COPY *.sh /
RUN chmod +x /*.sh

COPY etc-hosts.tmpl /etc/etc-hosts.tmpl

#修正因为备份/var/lib/docker导致的目录权限错误
RUN chmod 777 /tmp

VOLUME /var/lib/pgsql/data
VOLUME /hadoop/hdfs/
VOLUME /hadoop/zookeeper/
VOLUME /data/hawq/
#docker build --rm -t incloud/ambari-hawq:patch .

#HUE安装
RUN yum -y install wget tar asciidoc krb5-devel cyrus-sasl-gssapi cyrus-sasl-devel libxml2-devel libxslt-devel libtidy mysql mysql-devel openldap-devel python-devel python-simplejson python-setuptools sqlite-devel gcc gcc-c++ rsync saslwrapper-devel pycrypto gmp-devel libyaml-devel cyrus-sasl-plain cyrus-sasl-devel cyrus-sasl-gssapi
RUN yum -y install postgresql-devel python-psycopg2
COPY hue/hue-3.9.tgz /usr/local/
RUN cd /usr/local/ && tar -zxf hue-3.9.tgz && rm -rf hue-3.9.tgz
COPY hue/HUE/ /var/lib/ambari-server/resources/stacks/HDP/2.3/services/HUE/
#在hawq master上执行
#RUN echo "host  all gpadmin 0.0.0.0/0 trust" >> /data/hawq/master/pg_hba.conf

