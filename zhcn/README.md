# 说明
在jiadx/ambari-hawq基础上增加中文支持，修改 /etc/sysconfig/i18n 文件。


# 构建

docker build --rm -t incloud/ambari-hawq:zh_CN .

# 使用

与[ambari-hawq]相同。


查看文件是否可正常显示中文：
cat /opt/ambari-hawq/hawq/y2013-9.csv