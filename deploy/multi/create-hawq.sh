#!/usr/bin/env bash
export CLUSTER="cluster1"
#-----1.创建hadoop集群，包括：HDFS、YARN
curl --user admin:admin -H 'X-Requested-By:ambari' -X POST http://localhost:8080/api/v1/blueprints/bp-for-hawq-multi \
                       -d @bp-for-hawq-multi.json
#删除bp
#curl --user admin:admin -H 'X-Requested-By:ambari' -X DELETE http://localhost:8080/api/v1/blueprints/bp-for-hawq-multi

curl --user admin:admin -H 'X-Requested-By:ambari' -X POST http://localhost:8080/api/v1/clusters/$CLUSTER \
        -d @cluster-deploy.json


#----2.
