#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import grp
import pwd
from resource_management import *

from hue_service import hue_service


class Master(Script):

  #Call setup_hue.sh to install the service
  def install(self, env):
  
    #import properties defined in -config.xml file from params class
    import params
    import status_params
    env.set_params(params)  
    # Install packages listed in metainfo.xml
    self.install_packages(env)
    
    Execute('find ' + params.service_packagedir + ' -iname "*.sh" | xargs chmod +x')

    try: grp.getgrnam(params.hue_group)
    except KeyError: Group(group_name=params.hue_group) 
    
    try: pwd.getpwnam(params.hue_user)
    except KeyError: User(username=params.hue_user,
                          gid=params.hue_group,
                          groups=[params.hue_group],
                          ignore_failures=True)    
    Directory([params.hue_log_dir, status_params.hue_piddir],
              mode=0755,
              cd_access='a',
              owner=params.hue_user,
              group=params.hue_group,
              recursive=True
              )
    File(params.hue_log,
         mode=0644,
         owner=params.hue_user,
         group=params.hue_group,
         content=''
         )

    Execute('echo Hue dir: ' + params.hue_dir)
    #Execute('cd ' + params.hue_install_dir + '; rm -rf hue*')
    #Execute('cd ' + params.hue_install_dir + '; cat /etc/yum.repos.d/HD.repo | grep "baseurl" | awk -F \'=\' \'{print $2"hue/hue-3.9.tgz"}\' | xargs wget -O hue.tgz -a ' + params.hue_log)
    #Execute('cd ' + params.hue_install_dir + '; tar -zxvf hue.tgz')
    Execute(format("ln -s {hue_dir}/desktop/libs/hadoop/java-lib/hue-plugins-3.9.0-SNAPSHOT.jar /usr/hdp/current/hadoop-client/lib"), ignore_failures=True)
    #Execute('cd ' + params.hue_install_dir + '; rm -rf hue.tgz')
    Execute('cd ' + params.hue_install_dir + '; ln -s hue* latest', user=params.hue_user)
    if params.hue_bindir == 'UNDEFINED':
      Execute('echo Error: hue_bin: ' + params.hue_bindir)
        
    #ensure all Hue files owned by hue
    Execute('chown -R ' + params.hue_user + ':' + params.hue_group + ' ' + params.hue_dir)
    #add environment variable
    Execute(format("{service_packagedir}/scripts/add_env_variable.sh"), ignore_failures=True)   
    Execute ('echo "Hue install complete"')



  def configure(self, env):
    import params
    env.set_params(params)
    
    Execute (format("mkdir {hue_eachconf}; rm -rf {hue_conf}/hue.ini"), user=params.hue_user) 

    log_content=InlineTemplate(params.hue_log_content)    
    File(format("{hue_conf}/log.conf"), content=log_content, owner=params.hue_user) 

    #write content field to hue.ini  
    desktop_content=InlineTemplate(params.hue_desktop_content)
    File(format("{hue_eachconf}/hue.desktop.txt"), content=desktop_content, owner=params.hue_user)

    notebook_content=InlineTemplate(params.hue_notebook_content)
    File(format("{hue_eachconf}/hue.notebook.txt"), content=notebook_content, owner=params.hue_user)

    hadoop_content=InlineTemplate(params.hue_hadoop_content)
    File(format("{hue_eachconf}/hue.hadoop.txt"), content=hadoop_content, owner=params.hue_user)

    hive_content=InlineTemplate(params.hue_hive_content)
    File(format("{hue_eachconf}/hue.hive.txt"), content=hive_content, owner=params.hue_user)

    spark_content=InlineTemplate(params.hue_spark_content)
    File(format("{hue_eachconf}/hue.spark.txt"), content=spark_content, owner=params.hue_user)

    oozie_content=InlineTemplate(params.hue_oozie_content)
    File(format("{hue_eachconf}/hue.oozie.txt"), content=oozie_content, owner=params.hue_user)

    pig_content=InlineTemplate(params.hue_pig_content)
    File(format("{hue_eachconf}/hue.pig.txt"), content=pig_content, owner=params.hue_user)

    hbase_content=InlineTemplate(params.hue_hbase_content)
    File(format("{hue_eachconf}/hue.hbase.txt"), content=hbase_content, owner=params.hue_user)

    solr_content=InlineTemplate(params.hue_solr_content)
    File(format("{hue_eachconf}/hue.solr.txt"), content=solr_content, owner=params.hue_user)

    zookeeper_content=InlineTemplate(params.hue_zookeeper_content)
    File(format("{hue_eachconf}/hue.zookeeper.txt"), content=zookeeper_content, owner=params.hue_user)

    rdbms_content=InlineTemplate(params.hue_rdbms_content)
    File(format("{hue_eachconf}/hue.rdbms.txt"), content=rdbms_content, owner=params.hue_user)
    
    Execute (format("cat {hue_eachconf}/hue.*.txt >> {hue_conf}/hue.ini"), user=params.hue_user) 
    


  #Call start.sh to start the service
  def start(self, env):

    #import properties defined in -config.xml file from params class
    import params
    #import status properties defined in -env.xml file from status_params class
    import status_params
    self.configure(env)

    #this allows us to access the params.hue_pidfile property as format('{hue_pidfile}')
    env.set_params(params)
        
    Execute('find ' + params.service_packagedir + ' -iname "*.sh" | xargs chmod +x')

    #setup hue
    #form command to invoke setup_hue.sh with its arguments and execute it
    cmd = format("{service_packagedir}/scripts/setup_hue.sh {hue_dir} {hue_user} >> {hue_log}")
    Execute('echo "Running ' + cmd + '" as root')
    Execute(cmd, user=params.hue_user, ignore_failures=True)
    #start hue
    #form command to invoke start.sh with its arguments and execute it
    Execute (format("rm -f {hue_pidfile} >> {hue_log}"), user=params.hue_user, ignore_failures=True)
    cmd = params.service_packagedir + '/scripts/start.sh ' + params.hue_dir + ' ' + params.hue_log + ' ' + status_params.hue_pidfile + ' ' + params.hue_bindir
    Execute('echo "Running cmd: ' + cmd + '"')   
    Execute(cmd, user=params.hue_user)
      

  #Called to stop the service using the pidfile
  def stop(self, env):
    import params
    #import status properties defined in -env.xml file from status_params class  
    #this allows us to access the params.hue_pidfile property as format('{hue_pidfile}')
    env.set_params(params)
    #self.configure(env)
    
    #kill the instances of hue
    Execute (format("cat {hue_pidfile} | xargs kill -9"), user=params.hue_user, ignore_failures=True)  
    #delete the pid file
    Execute (format("rm -f {hue_pidfile} >> {hue_log}"), user=params.hue_user, ignore_failures=True)
    #File({hue_pidfile}, action = "delete", owner = params.hue_user)

  #Called to get status of the service using the pidfile
  def status(self, env):

    #import status properties defined in -env.xml file from status_params class
    import status_params
    env.set_params(status_params)     
    #use built-in method to check status using pidfile
    check_process_status(status_params.hue_pidfile) 
  
  def startlivyserver(self, env):
    import params
    env.set_params(params)
    #Execute (format("hadoop fs -put {hue_dir}/apps/spark/java-lib/livy-assembly.jar /user/oozie/share/lib/livy"),ignore_failures=True) 
    hue_service('livy_server', 'livy', action = 'start')
 
  def stoplivyserver(self, env):
    import params
    env.set_params(params)
    hue_service('livy_server', 'livy',  action = 'stop')

  def usersync(self, env):
    import params
    env.set_params(params)
    Execute (format("{hue_bindir}/hue useradmin_sync_with_unix"), user=params.hue_user) 

if __name__ == "__main__":
  Master().execute()
