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
import re
import os
import time
import crypt
import filecmp
from resource_management.libraries.resources.xml_config import XmlConfig
from resource_management.core.resources.system import Execute, Directory, File
from resource_management.core.logger import Logger
from resource_management.core.system import System
from resource_management.core.exceptions import Fail
from resource_management.core.resources.accounts import Group, User
from resource_management.core.source import Template
import xml.etree.ElementTree as ET

import utils
import hawqconstants


def update_bashrc(source_file, target_file):
  """
  Updates the hawq_user's .bashrc file with HAWQ env variables like
  MASTER_DATA_DIRECTORY, PGHOST, PGPORT and PGUSER. 
  And sources the greenplum_path file.
  """
  append_src_cmd = "echo 'source {0}' >> {1}".format(source_file, target_file)
  src_cmd_exists = "grep 'source {0}' {1}".format(source_file, target_file)
  Execute(append_src_cmd, user=hawqconstants.hawq_user, timeout=hawqconstants.default_exec_timeout, not_if=src_cmd_exists)


def setup_user():
  """
  Creates HAWQ user home directory and sets up the correct ownership.
  """
  __create_hawq_user()
  __set_home_dir_ownership()


def __create_hawq_user():
  """
  Creates HAWQ user with default password and group.
  """
  import params
  Group(hawqconstants.hawq_group, ignore_failures=True)

  User(hawqconstants.hawq_user,
       gid=hawqconstants.hawq_group,
       password=crypt.crypt(hawqconstants.hawq_password, "salt"),
       groups=[hawqconstants.hawq_group, params.user_group],
       ignore_failures=True)


def __set_home_dir_ownership():
  """
  Updates the HAWQ user home directory to be owned by gpadmin:gpadmin.
  """
  command = "chown -R {0}:{1} {2}".format(hawqconstants.hawq_user, hawqconstants.hawq_group, hawqconstants.hawq_home_dir)
  Execute(command, timeout=hawqconstants.default_exec_timeout)


def setup_common_configurations():
  """
  Sets up the config files common to master, standby and segment nodes.
  """
  import params

  substituted_conf_dict = __substitute_hostnames_in_hawq_site()
  XmlConfig("hawq-site.xml",
            conf_dir=hawqconstants.hawq_config_dir,
            configurations=substituted_conf_dict,
            configuration_attributes=params.config['configuration_attributes']['hawq-site'],
            owner=hawqconstants.hawq_user,
            group=hawqconstants.hawq_group,
            mode=0644)
  __set_osparams()


def __substitute_hostnames_in_hawq_site():
  """
  Temporary function to replace localhost with actual HAWQ component hostnames.
  This function will be in place till the entire HAWQ plugin code along with the UI
  changes are submitted to the trunk.
  """
  import params

  LOCALHOST = "localhost"
  
  # in case there is no standby
  hawqstandby_host_desired_value = params.hawqstandby_host if params.hawqstandby_host is not None else 'none' 
  
  substituted_hawq_site = params.hawq_site.copy()
  hawq_site_property_map = {"hawq_master_address_host": params.hawqmaster_host,
                            "hawq_standby_address_host": hawqstandby_host_desired_value,
                            "hawq_rm_yarn_address": params.rm_host,
                            "hawq_rm_yarn_scheduler_address": params.rm_host,
                            "hawq_dfs_url": params.namenode_host
                            }

  for property, desired_value in hawq_site_property_map.iteritems():
    if desired_value is not None:
      # Replace localhost with required component hostname
      substituted_hawq_site[property] = re.sub(LOCALHOST, desired_value, substituted_hawq_site[property])

  return substituted_hawq_site


def __set_osparams():
  """
  Updates parameters in sysctl.conf and limits.conf required by HAWQ.
  """
  # Create a temp scratchpad directory
  utils.create_dir_as_hawq_user(hawqconstants.hawq_tmp_dir)

  # Suse doesn't supports loading values from files in /etc/sysctl.d
  # So we will have to directly edit the sysctl file
  if System.get_instance().os_family == "suse":
    # Update /etc/sysctl.conf
    __update_sysctl_file_suse()
  else:
    # Update /etc/sysctl.d/hawq.conf
    __update_sysctl_file()

  __update_limits_file()


def __update_limits_file():
  """
  Updates /etc/security/limits.d/hawq.conf file with the HAWQ parameters.
  """
  import params
  # Ensure limits directory exists
  Directory(hawqconstants.limits_conf_dir, recursive=True, owner=hawqconstants.root_user, group=hawqconstants.root_user)

  # Generate limits for hawq user
  limits_file_content = "#### HAWQ Limits Parameters  ###########\n"
  for key, value in params.hawq_limits.iteritems():
    if not __valid_input(value):
      raise Exception("Value {0} for parameter {1} contains non-numeric characters which are not allowed (except whitespace), please fix the value and retry".format(value, key))
    """
    Content of the file to be written should be of the format
    gpadmin soft nofile 290000
    gpadmin hard nofile 290000
    key used in the configuration is of the format soft_nofile, thus strip '_' and replace with 'space'
    """
    limits_file_content += "{0} {1} {2}\n".format(hawqconstants.hawq_user, re.sub("_", " ", key), value.strip())
  File('{0}/{1}.conf'.format(hawqconstants.limits_conf_dir, hawqconstants.hawq_user), content=limits_file_content,
       owner=hawqconstants.hawq_user, group=hawqconstants.hawq_group)


def __valid_input(value):
  """
  Validate if input value contains number (whitespaces allowed), return true if found else false
  """
  return re.search("^ *[0-9][0-9 ]*$", value)


def __convert_sysctl_dict_to_text():
  """
  Convert sysctl configuration dict to text with each property value pair separated on new line
  """
  import params
  sysctl_file_content = "### HAWQ System Parameters ###########\n"
  for key, value in params.hawq_sysctl.iteritems():
    if not __valid_input(value):
      raise Exception("Value {0} for parameter {1} contains non-numeric characters which are not allowed (except whitespace), please fix the value and retry".format(value, key))
    sysctl_file_content += "{0} = {1}\n".format(key, value)
  return sysctl_file_content


def __update_sysctl_file():
  """
  Updates /etc/sysctl.d/hawq_sysctl.conf file with the HAWQ parameters on CentOS/RHEL.
  """
  # Ensure sys ctl sub-directory exists
  Directory(hawqconstants.sysctl_conf_dir, recursive=True, owner=hawqconstants.root_user, group=hawqconstants.root_user)

  # Generate temporary file with kernel parameters needed by hawq
  File(hawqconstants.hawq_sysctl_tmp_file, content=__convert_sysctl_dict_to_text(), owner=hawqconstants.hawq_user,
       group=hawqconstants.hawq_group)

  is_changed = True
  if os.path.exists(hawqconstants.hawq_sysctl_tmp_file) and os.path.exists(hawqconstants.hawq_sysctl_file):
    is_changed = not filecmp.cmp(hawqconstants.hawq_sysctl_file, hawqconstants.hawq_sysctl_tmp_file)

  if is_changed:
    # Generate file with kernel parameters needed by hawq, only if something
    # has been changed by user
    Execute("cp -p {0} {1}".format(hawqconstants.hawq_sysctl_tmp_file, hawqconstants.hawq_sysctl_file))

    # Reload kernel sysctl parameters from hawq file.
    Execute("sysctl -e -p {0}".format(hawqconstants.hawq_sysctl_file), timeout=hawqconstants.default_exec_timeout)

  # Wipe out temp file
  File(hawqconstants.hawq_sysctl_tmp_file, action='delete')


def __update_sysctl_file_suse():
  """
  Updates /etc/sysctl.conf file with the HAWQ parameters on SUSE.
  """
  # Backup file
  backup_file_name = hawqconstants.sysctl_backup_file.format(str(int(time.time())))
  try:
    # Generate file with kernel parameters needed by hawq to temp file
    File(hawqconstants.hawq_sysctl_tmp_file, content=__convert_sysctl_dict_to_text(), owner=hawqconstants.hawq_user,
         group=hawqconstants.hawq_group)

    sysctl_file_dict = utils.read_file_to_dict(hawqconstants.sysctl_suse_file)
    sysctl_file_dict_original = sysctl_file_dict.copy()
    hawq_sysctl_dict = utils.read_file_to_dict(hawqconstants.hawq_sysctl_tmp_file)

    # Merge common system file with hawq specific file
    sysctl_file_dict.update(hawq_sysctl_dict)

    if sysctl_file_dict_original != sysctl_file_dict:
      # Backup file
      Execute("cp {0} {1}".format(hawqconstants.sysctl_suse_file, backup_file_name), timeout=hawqconstants.default_exec_timeout)
      # Write merged properties to file
      utils.write_dict_to_file(sysctl_file_dict, hawqconstants.sysctl_suse_file)
      # Reload kernel sysctl parameters from /etc/sysctl.conf
      Execute("sysctl -e -p", timeout=hawqconstants.default_exec_timeout)

  except Exception as e:
    Logger.error("Error occurred while updating sysctl.conf file, reverting the contents" + str(e))
    Execute("cp {0} {1}".format(hawqconstants.sysctl_suse_file, hawqconstants.hawq_sysctl_tmp_file))
    Execute("mv {0} {1}".format(backup_file_name, hawqconstants.sysctl_suse_file), timeout=hawqconstants.default_exec_timeout)
    Logger.error("Please execute `sysctl -e -p` on the command line manually to reload the contents of file {0}".format(
      hawqconstants.hawq_sysctl_tmp_file))
    raise Fail("Failed to update sysctl.conf file ")


def get_local_hawq_site_property(property_name):
  """
  Fetches the value of the property specified, from the local hawq-site.xml.
  """
  hawq_site_path = None
  try:
    hawq_site_path = os.path.join(hawqconstants.hawq_config_dir, "hawq-site.xml")
    hawq_site_root = ET.parse(hawq_site_path).getroot()
    for property in hawq_site_root.findall("property"):
      for item in property:
        if item.tag == 'name':
          current_property_name = item.text.strip() if item and item.text else item.text
        elif item.tag == 'value':
          current_property_value = item.text.strip() if item and item.text else item.text
      if property_name == current_property_name:
          return current_property_value
    raise #If property has not been found
  except Exception:
    raise Fail("Unable to read property {0} from local {1}".format(property_name, hawq_site_path))

def validate_configuration():
  """
  Validates if YARN is present in the configuration when the user specifies YARN as HAWQ's resource manager.
  """
  import params

  # At this point, hawq should be included.
  if 'hawq-site' not in params.config['configurations']:
    raise Fail("Configurations does not contain hawq-site. Please include HAWQ")

  # If HAWQ is set to use YARN and YARN is not configured, error.
  rm_type = params.config["configurations"]["hawq-site"].get("hawq_global_rm_type")
  if rm_type == "yarn" and "yarn-site" not in params.config["configurations"]:
    raise Fail("HAWQ is set to use YARN but YARN is not deployed. " + 
               "hawq_global_rm_type property in hawq-site is set to 'yarn' but YARN is not configured. " + 
               "Please deploy YARN before starting HAWQ or change the value of hawq_global_rm_type property to 'none'")
