#!/usr/bin/env bash
export CLUSTER="cluster1"
#-----1.创建hadoop集群，包括：HDFS、YARN
curl --user admin:admin -H 'X-Requested-By:ambari' -X POST http://localhost:8080/api/v1/blueprints/bp-for-hawq \
                       -d @bp-for-hawq.json
#删除bp
#curl --user admin:admin -H 'X-Requested-By:ambari' -X DELETE http://localhost:8080/api/v1/blueprints/bp-for-hawq

curl --user admin:admin -H 'X-Requested-By:ambari' -X POST http://localhost:8080/api/v1/clusters/$CLUSTER \
        -d @cluster-deploy.json


#----2.
