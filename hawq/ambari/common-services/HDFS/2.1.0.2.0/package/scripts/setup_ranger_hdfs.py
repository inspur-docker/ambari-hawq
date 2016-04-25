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
import os
from resource_management.core.logger import Logger
from resource_management.core.resources.system import Execute
from resource_management.libraries.functions.constants import Direction
from resource_management.libraries.functions.format import format
from resource_management.libraries.functions.version import compare_versions

def setup_ranger_hdfs(upgrade_type=None):
  import params

  if params.has_ranger_admin:

    if params.xml_configurations_supported:
      from resource_management.libraries.functions.setup_ranger_plugin_xml import setup_ranger_plugin
    else:
      from resource_management.libraries.functions.setup_ranger_plugin import setup_ranger_plugin

    hdp_version = None

    if upgrade_type is not None:
      hdp_version = params.version

    if params.retryAble:
      Logger.info("HDFS: Setup ranger: command retry enables thus retrying if ranger admin is down !")
    else:
      Logger.info("HDFS: Setup ranger: command retry not enabled thus skipping if ranger admin is down !")

    setup_ranger_plugin('hadoop-client', 'hdfs',
                        params.downloaded_custom_connector, params.driver_curl_source,
                        params.driver_curl_target, params.java_home,
                        params.repo_name, params.hdfs_ranger_plugin_repo,
                        params.ranger_env, params.ranger_plugin_properties,
                        params.policy_user, params.policymgr_mgr_url,
                        params.enable_ranger_hdfs, conf_dict=params.hadoop_conf_dir,
                        component_user=params.hdfs_user, component_group=params.user_group, cache_service_list=['hdfs'],
                        plugin_audit_properties=params.config['configurations']['ranger-hdfs-audit'], plugin_audit_attributes=params.config['configuration_attributes']['ranger-hdfs-audit'],
                        plugin_security_properties=params.config['configurations']['ranger-hdfs-security'], plugin_security_attributes=params.config['configuration_attributes']['ranger-hdfs-security'],
                        plugin_policymgr_ssl_properties=params.config['configurations']['ranger-hdfs-policymgr-ssl'], plugin_policymgr_ssl_attributes=params.config['configuration_attributes']['ranger-hdfs-policymgr-ssl'],
                        component_list=['hadoop-client'], audit_db_is_enabled=params.xa_audit_db_is_enabled,
                        credential_file=params.credential_file, xa_audit_db_password=params.xa_audit_db_password, 
                        ssl_truststore_password=params.ssl_truststore_password, ssl_keystore_password=params.ssl_keystore_password,
                        hdp_version_override = hdp_version, skip_if_rangeradmin_down= not params.retryAble)

    if hdp_version and params.upgrade_direction == Direction.UPGRADE:
      # when upgrading to 2.3+, this env file must be removed
      if compare_versions(hdp_version, '2.3', format=True) > 0:
        source_file = os.path.join(params.hadoop_conf_dir, 'set-hdfs-plugin-env.sh')
        target_file = source_file + ".bak"
        Execute(("mv", source_file, target_file), sudo=True, only_if=format("test -f {source_file}"))
  else:
    Logger.info('Ranger admin not installed')

def create_ranger_audit_hdfs_directories(check):
  import params

  if params.has_ranger_admin:
    if params.xml_configurations_supported and params.enable_ranger_hdfs and params.xa_audit_hdfs_is_enabled:
      params.HdfsResource("/ranger/audit",
                         type="directory",
                         action="create_on_execute",
                         owner=params.hdfs_user,
                         group=params.hdfs_user,
                         mode=0755,
                         recursive_chmod=True,
                         only_if=check
      )
      params.HdfsResource("/ranger/audit/hdfs",
                         type="directory",
                         action="create_on_execute",
                         owner=params.hdfs_user,
                         group=params.hdfs_user,
                         mode=0700,
                         recursive_chmod=True,
                         only_if=check
      )
      params.HdfsResource(None, action="execute", only_if=check)
  else:
    Logger.info('Ranger admin not installed')
