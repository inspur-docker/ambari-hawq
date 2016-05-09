# Readme
install hadoop_2.3 && hawq && depends .

install ambari-server

Bug fixes : rename hawq services script "constants.py -> hawqconstants.py"

more detail -> [chinese readme]

# Get Hawq RPM
from :

    https://network.pivotal.io/products/pivotal-hdb。

or

    ./PIVOTAL-HDB/

# Get image
build :

    $ docker build  --rm -t incloud/ambari-hawq .
or pull：

    $ docker pull incloud/ambari-hawq

# deploy with compose

    $ cd deploy/multi
    $ docker-compose up -d


# create hadoop cluster

    $ docker exec -ti multi_ambari-server_1 bash
in container :

    /opt/ambari-hawq/create-hawq.sh
# hawq test

    $ docker exec -ti  multi_hawq-master_1 bash
in container:

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

# chinese support for hawq

    docker pull  incloud/ambari-hawq:zh_CN

# all in one deploy



# production deploy

 [chinese readme]: /readme_cn.md