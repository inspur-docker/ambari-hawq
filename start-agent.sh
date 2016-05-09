#!/bin/bash
chown -R gpadmin:gpadmin /data/hawq
service sshd start
service ntpd start

if [[ $1 == "reset" ]]; then
  ambari-agent reset $2
fi

ambari-agent restart &

#start docker-gen in master node
HADOOP_ROLE=${HADOOP_ROLE:-slave}
if [ "$HADOOP_ROLE" = "master" ]; then
  DOCKER_URI=${DOCKER_URI:-unix:///var/run/docker.sock}
  docker-gen  -endpoint $DOCKER_URI  -watch -notify "/add-hosts.sh /etc/hosts.new" /etc/etc-hosts.tmpl /etc/hosts.new &
fi

while [ 1 ]
do
   tail -f /var/log/ambari-agent/ambari-agent.log
   sleep 10
done