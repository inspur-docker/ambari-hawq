1.进入hawq-master容器

2.首次执行-创建数据库
su gpadmin
source /usr/local/hawq/greenplum_path.sh
createdb

3.建表测试：
$ psql
psql (8.2.15)
Type "help" for help.

gpadmin=#
CREATE TABLE my_table ( first integer not null default 0,second text);

insert into my_table values(1,'hello');
insert into my_table values(2,'world');
select * from my_table;


4.pxf测试

CREATE EXTERNAL TABLE ext_aqi(seq integer,city text, aqi integer,quality text)
        LOCATION ('pxf://localhost:51200/test/aqi'
                  '?PROFILE=HdfsTextSimple')
       FORMAT 'CSV';

5.目录
GPHOME地址：/usr/local/hawq