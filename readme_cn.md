# 说明
   1.本镜像基于[ambari-docker]项目的`incloud/ambari-agent`镜像，并预安装hadoop_2.3、hawq及相关依赖，可以加快ambari集群创建时的hadoop相关软件安装。

   2.同时安装ambari-server，增加HAWQ服务，可以all in one 部署。

   3.修正hawq service的bug：在同时安装了ambari-server、ambari-agent时，
   HAWQ服务的状态检查有问题，不能正确执行。原因是HAWQ服务的python脚本引用了`import constants`，
   而这个`constants`并没有引用到HAWQ服务目录的文件-`/var/lib/ambari-server/resources/common-services/HAWQ/2.0.0/package/scripts/constants.py`，而是引用到`/usr/lib/python2.6/site-packages/resource_monitoring/ambari_commons/constants.py`

   4.修改star-agent.sh，在启动时根据hawq需求生成/etc/security/limits.conf文件。
## 获取镜像
构建

    $ docker build  --rm -t incloud/ambari-hawq .
或pull：

    $ docker pull incloud/ambari-hawq

## 启用docker容器的DNS服务发现
   参见 [docker-dns-gen] 项目。

## 使用compose启动多个容器节点：
由于需要修改内核参数，需要`--privileged`启动容器。

    cd deploy/multi
    docker-compose up -d

## 创建hadoop+hawq集群:
  进入ambari-server容器

    $ docker exec -ti multi_ambari-server_1 bash
  在容器内执行

    $ /opt/ambari-hawq/create-hawq.sh

## hawq测试
  进入hawq master节点

    $ docker exec -ti  multi_hawq-master_1 bash
  在master节点内执行：

    $ su gpadmin
    $ source /usr/local/hawq/greenplum_path.sh
    $ createdb

    $ psql

    psql (8.2.15)
    Type "help" for help.

    gpadmin=#
             CREATE TABLE my_table ( first integer not null default 0,second text);

             insert into my_table values(1,'hello');
             insert into my_table values(2,'world');
             select * from my_table;
             insert into my_table values(3,'three');
## 中文语言支持
在使用hawq插入中文数据时会出现错误，原因是容器环境没有安装中文支持，
可参考[zhcn/Dockerfile]制作支持中文的镜像。
## 注意
repo/目录下的文件使用了本地资源库，需根据环境调整。

hawq rpm包下载自https://network.pivotal.io/products/pivotal-hdb#/releases/1503/file_groups/380，并制作本地repo资源库。

  [docker-dns-gen]: https://github.com/jiadexin/docker-dns-gen
  [ambari-docker]: https://github.com/inspur-docker/ambari-docker
  [zhcn/Dockerfile]: zhcn/Dockerfile