#!/bin/bash
chown -R postgres:postgres /var/lib/pgsql/data

service sshd start

if [[ $1 == "setup" ]]; then
  ambari-server setup -s -j $JAVA_HOME
fi

ambari-server restart &

#start docker-gen in master node
HADOOP_ROLE=${HADOOP_ROLE:-slave}
if [ "$HADOOP_ROLE" = "master" ]; then
  DOCKER_URI=${DOCKER_URI:-unix:///var/run/docker.sock}
  docker-gen  -endpoint $DOCKER_URI  -watch -notify "/add-hosts.sh /etc/hosts.new" /etc/etc-hosts.tmpl /etc/hosts.new &
fi

while [ 1 ]
do
    tail -f /var/log/ambari-server/ambari-server.log
	sleep 10
done