FROM incloud/ambari-hawq:zh_CN

COPY *.py /var/lib/ambari-server/resources/stacks/HDP/2.3/services/HUE/package/scripts/
#RUN cd /usr/local && ln -s hue* latest
#docker build --rm -t incloud/ambari-hawq:patch .

#在hawq master上执行
#RUN echo "host  all gpadmin 0.0.0.0/0 trust" >> /data/hawq/master/pg_hba.conf