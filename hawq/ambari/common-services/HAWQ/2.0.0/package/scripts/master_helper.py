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
import os
from resource_management.core.resources.system import File, Execute
from resource_management.core.source import Template
from resource_management.core.exceptions import Fail
from resource_management.core.logger import Logger

import utils
import common
import hawqconstants

def __setup_master_specific_conf_files():
  """
  Sets up config files only applicable for HAWQ Master and Standby nodes
  """
  import params

  File(hawqconstants.hawq_check_file, content=params.gpcheck_content, owner=hawqconstants.hawq_user, group=hawqconstants.hawq_group,
       mode=0644)

  File(hawqconstants.hawq_slaves_file, content=Template("slaves.j2"), owner=hawqconstants.hawq_user, group=hawqconstants.hawq_group,
       mode=0644)

  File(hawqconstants.hawq_hosts_file, content=Template("hawq-hosts.j2"), owner=hawqconstants.hawq_user, group=hawqconstants.hawq_group,
       mode=0644)


def __setup_passwordless_ssh():
  """
  Exchanges ssh keys to setup passwordless ssh for the hawq_user between the HAWQ Master and the HAWQ Segment nodes
  """
  utils.exec_hawq_operation("ssh-exkeys", "-f {0} -p {1}".format(hawqconstants.hawq_hosts_file, hawqconstants.hawq_password))

  File(hawqconstants.hawq_hosts_file, action='delete')


def __setup_hawq_user_profile():
  """
  Sets up the ENV variables for hawq_user as a convenience for the command line users
  """
  hawq_profile_file = os.path.join(os.path.expanduser("~{0}".format(hawqconstants.hawq_user)), ".hawq-profile.sh")
  File(hawq_profile_file, content=Template("hawq-profile.sh.j2"), owner=hawqconstants.hawq_user, group=hawqconstants.hawq_group)
  common.update_bashrc(hawq_profile_file, hawqconstants.hawq_user_bashrc_file)


def configure_master():
  """
  Configures the master node after rpm install
  """
  common.setup_user()
  common.setup_common_configurations()
  __setup_master_specific_conf_files()
  __setup_hawq_user_profile()
  __create_local_dirs()


def __create_local_dirs():
  """
  Creates the required local directories for HAWQ 
  """
  import params
  # Create Master directories
  utils.create_dir_as_hawq_user(params.hawq_master_dir)
  utils.create_dir_as_hawq_user(params.hawq_master_temp_dir.split(','))

  Execute("chown {0}:{1} {2}".format(hawqconstants.hawq_user, hawqconstants.hawq_group, os.path.dirname(params.hawq_master_dir)),
          user=hawqconstants.root_user, timeout=hawqconstants.default_exec_timeout)

  Execute("chmod 700 {0}".format(params.hawq_master_dir), user=hawqconstants.root_user, timeout=hawqconstants.default_exec_timeout)


def __create_hdfs_dirs():
  """
  Creates the required HDFS directories for HAWQ
  """
  import params
  params.HdfsResource(params.hawq_hdfs_data_dir, type="directory", action="create_on_execute", owner=hawqconstants.hawq_user, group=hawqconstants.hawq_group, mode=0755)
  params.HdfsResource(None, action="execute")


def __init_active():
  """
  Initializes the active master
  """
  __create_hdfs_dirs()
  utils.exec_hawq_operation(hawqconstants.INIT, "{0} -a -v".format(hawqconstants.MASTER))


def __init_standby():
  """
  Initializes the HAWQ Standby Master
  """
  utils.exec_hawq_operation(hawqconstants.INIT, "{0} -a -v".format(hawqconstants.STANDBY))


def __get_component_name():
  """
  Identifies current node as either HAWQ Master or HAWQ Standby Master
  """
  return hawqconstants.MASTER if __is_active_master() else hawqconstants.STANDBY


def __start_local_master():
  """
  Starts HAWQ Master or HAWQ Standby Master component on the host
  """
  import params
  component_name = __get_component_name()
  utils.exec_hawq_operation(
        hawqconstants.START,
        "{0} -a".format(component_name),
        not_if=utils.chk_hawq_process_status_cmd(params.hawq_master_address_port, component_name))

  
def __is_local_initialized():
  """
  Checks if the local node has been initialized
  """
  import params
  return os.path.exists(os.path.join(params.hawq_master_dir, hawqconstants.postmaster_opts_filename))


def __get_standby_host():
  """
  Returns the name of the HAWQ Standby Master host from hawq-site.xml, or None if no standby is configured
  """
  standby_host = common.get_local_hawq_site_property("hawq_standby_address_host")
  return None if standby_host is None or standby_host.lower() == 'none' else standby_host


def __is_standby_initialized():
  """
  Returns True if HAWQ Standby Master is initialized, False otherwise
  """
  import params
  
  file_path = os.path.join(params.hawq_master_dir, hawqconstants.postmaster_opts_filename)
  (retcode, _, _) = utils.exec_ssh_cmd(__get_standby_host(), "[ -f {0} ]".format(file_path))
  return retcode == 0


def start_master():
  """
  Initializes HAWQ Master/Standby if not already done and starts them
  """
  import params

  if not params.hostname in [params.hawqmaster_host, params.hawqstandby_host]:
    Fail("Host should be either active Hawq master or Hawq standby.")

  is_active_master = __is_active_master()
  # Exchange ssh keys from active hawq master before starting.
  if is_active_master:
    __setup_passwordless_ssh()

  if __is_local_initialized():
    __start_local_master()

  elif is_active_master:
    __init_active()

  if is_active_master and __get_standby_host() is not None and not __is_standby_initialized():
    __init_standby()


def stop_master():
  """
  Stops the HAWQ Master/Standby
  """
  import params
  component_name = __get_component_name()
  utils.exec_hawq_operation(
                hawqconstants.STOP,
                "{0} -a".format(component_name),
                only_if=utils.chk_hawq_process_status_cmd(params.hawq_master_address_port, component_name))


def __is_active_master():
  """
  Finds if this node is the active master
  """
  import params
  return params.hostname == common.get_local_hawq_site_property("hawq_master_address_host")
