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
      source /usr/local/hawq/greenplum_path.sh
      createdb

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

# 生产环境部署
主要解决hadoop、hawq、ambari数据持久化的问题。可使用`--volume`容器启动参数来绑定本地主机目录。
策略如下：

## 1.Hadoop数据

Namenode 持久化方案：a.固定在指定的主机 b.使用分布式存储。
相关参数设置及ambari中的默认值：

    dfs.namenode.name.dir=/hadoop/hdfs/namenode
    dfs.namenode.checkpoint.dir=/hadoop/hdfs/namesecondary

Datanode持久化方案：直接绑定主机目录。
相关目录：

    dfs.datanode.data.dir=/hadoop/hdfs/data
其他目录：

    hadoop.tmp.dir=/tmp/hadoop-${user.name}
    Hadoop Log Dir Prefix : /var/log/hadoop
    dfs.journalnode.edits.dir=/hadoop/hdfs/journalnode




## 2.Ambari
Ambari Server元数据： a.固定在指定主机 b.使用分布式存储。默认配置（/etc/ambari-server/conf/ambari.properties）：

     #主要元数据信息保存在数据库中，如postgre则默认目录为：
     /var/lib/pgsql/data

     security.server.keys_dir = /var/lib/ambari-server/keys
     #以下没有新增服务，应该不需要持久化
     resources.dir = /var/lib/ambari-server/resources
     shared.resources.dir = /usr/lib/ambari-server/lib/ambari_commons/resources
     custom.action.definitions = /var/lib/ambari-server/resources/custom_action_definitions

Ambari agent 数据： 不需要持久化？

    prefix = /var/lib/ambari-agent/data
    keysdir = /var/lib/ambari-agent/keys

日志：

    /var/log/ambari-server/
    /var/log/ambari-agent/
问题1：通过`--volume`指定的pgsql目录，在容器内初始化pgsql时总会出现数据目录的权限错误：
`initdb: could not access directory "/var/lib/pgsql/data": Permission denied`。

排查错误：不用`--volume`启动容器，初始化pgsql时仍然是权限错误。但该镜像是曾经成功执行过的。
后来通过与另外一台Docker主机的比较，发现`/var/lib/docker`目录下aufs文件系统的比较，发现有如下pgsql目录：

    find -name pgsql
    ./dfe63307baf13f0d0aa5fb73520b502af0c7face14a0b131a54c8e3d31a6ee55/var/lib/pgsql
    ./9227c27db4184e457463b34df9b0f0d02ca57c88203ceba83cd913ac590cafac/var/lib/pgsql
    ./9227c27db4184e457463b34df9b0f0d02ca57c88203ceba83cd913ac590cafac/etc/sysconfig/pgsql
    ./9227c27db4184e457463b34df9b0f0d02ca57c88203ceba83cd913ac590cafac/usr/lib64/pgsql
    ./9227c27db4184e457463b34df9b0f0d02ca57c88203ceba83cd913ac590cafac/usr/share/pgsql
然后查看目录权限，在正常运行的docker主机其目录权限是`26:tape`：

    ls ./9227c27db4184e457463b34df9b0f0d02ca57c88203ceba83cd913ac590cafac/var/lib/pgsql -l
    total 8
    drwx------ 2 26 tape 4096 Mar  2 11:58 backups
    drwx------ 2 26 tape 4096 Mar  2 11:58 data
而运行错误的镜像权限变成了`root:root`，原因：曾经把/var/lib/docker目录数据备份到其他目录，又迁移回来导致权限变更。

解决：

    1.重新下载镜像。
    2.手工设置镜像aufs的目录权限。
问题2：使用`--volume /data/psql:/var/lib/pgsql/data` 启动容器后，`/var/lib/pgsql/data`目录的权限还是会变成`root`。

解决：

    1.更改宿主机/data/psql权限： chown 26:tape /data/psql


## 3.hawq
Master元数据：a.固定在指定主机 b.使用分布式存储。

    master_data_directory=/data/hawq/master

Segment：不需要持久化？

    segment_data_directory=/data/hawq/segment

如果容器是删除`docker rm `或`docker-compose down`后重新运行`docker run`/`docker-compose up`，则需要持久的还要包括用户信息,会有如下问题：

Gpadmin用户目录-需要保存master到segment节点的gpadmin用户免登录设置（还需要增加gpadmin用户-在启动脚本执行？）:

    /home/gpadmin/.ssh/authorized_keys
PXF也需要增加用户，否则启动时有错误：

    resource_management.core.exceptions.Fail: Execution of 'useradd -m -s /bin/bash -G hdfs,hadoop,tomcat pxf' returned 6. useradd: group 'tomcat' does not exist
即使手工添加了这几个用户，还是会有错误：

    resource_management.core.exceptions.Fail: Applying File['/etc/pxf/conf/pxf-env.sh'] failed, parent directory /etc/pxf/conf doesn't exist

解决方案 ： 可以在ambari重新添加segment和PXF组件，如下：


    #停止并删除PXF服务
    curl -H 'X-Requested-By:hawq' -u admin:admin -X PUT -d '{"RequestInfo":{"context":"Stop Service"},"Body":{"ServiceInfo":{"state":"INSTALLED"}}}' http://localhost:8080/api/v1/clusters/cluster1/services/PXF
    curl -H 'X-Requested-By:hawq' -u admin:admin -X DELETE http://localhost:8080/api/v1/clusters/cluster1/services/PXF
    #通过界面或API再次添加服务
    curl -H 'X-Requested-By:hawq' --user admin:admin -i -X POST http://localhost:8080/api/v1/clusters/cluster1/services/PXF
    curl -H 'X-Requested-By:hawq' -u admin:admin -X POST http://localhost:8080/api/v1/clusters/cluster1/services/PXF/components/PXF
    #添加主机到组件
    curl -H 'X-Requested-By:hawq' -u admin:admin -i -X POST http://localhost:8080/api/v1/clusters/cluster1/hosts/hmaster/host_components/PXF
    curl -H 'X-Requested-By:hawq' -u admin:admin -i -X POST http://localhost:8080/api/v1/clusters/cluster1/hosts/hwork1/host_components/PXF
    curl -H 'X-Requested-By:hawq' -u admin:admin -i -X POST http://localhost:8080/api/v1/clusters/cluster1/hosts/hwork2/host_components/PXF
    curl -H 'X-Requested-By:hawq' -u admin:admin -i -X POST http://localhost:8080/api/v1/clusters/cluster1/hosts/hwork3/host_components/PXF
    #安装
    curl -H 'X-Requested-By:hawq' -u admin:admin -i -X PUT -d '{"HostRoles": {"state": "INSTALLED"}}' http://localhost:8080/api/v1/clusters/cluster1/hosts/hmaster/host_components/PXF
    curl -H 'X-Requested-By:hawq' -u admin:admin -i -X PUT -d '{"HostRoles": {"state": "INSTALLED"}}' http://localhost:8080/api/v1/clusters/cluster1/hosts/hwork1/host_components/PXF
    curl -H 'X-Requested-By:hawq' -u admin:admin -i -X PUT -d '{"HostRoles": {"state": "INSTALLED"}}' http://localhost:8080/api/v1/clusters/cluster1/hosts/hwork2/host_components/PXF
    curl -H 'X-Requested-By:hawq' -u admin:admin -i -X PUT -d '{"HostRoles": {"state": "INSTALLED"}}' http://localhost:8080/api/v1/clusters/cluster1/hosts/hwork3/host_components/PXF
或者只执行重新安装也可以？

否则在启动集群后需要在各segment节点执行：

    useradd gpadmin && su gpadmin
    ssh-keygen -q && cd /home/gpadmin/.ssh/ && scp hmaster:/home/gpadmin/.ssh/authorized_keys .


其他目录：

    log_filename=/home/gpadmin/hawqAdminLogs/hawq_init_20160422.log
    hawq_master_temp_directory=/tmp
    hawq_segment_temp_directory=/tmp

    hawq_re_cgroup_mount_point=/sys/fs/cgroup

## 4.zookeeper
数据目录：

    dataDir=/hadoop/zookeeper
其他：

    zk_log_dir=/var/log/zookeeper

## compose编排参考


# 自定义网桥
DOCKER主机A：

    --fixed-cidr=192.168.200.128/26
    地址范围;128-190
DOCKER主机B：

    --fixed-cidr=192.168.200.192/27
    地址范围;192-222
DOCKER主机C：

    --fixed-cidr=192.168.200.224/27
    地址范围;224-254



  [docker-dns-gen]: https://github.com/jiadexin/docker-dns-gen
  [ambari-docker]: https://github.com/inspur-docker/ambari-docker
  [zhcn/Dockerfile]: zhcn/Dockerfile