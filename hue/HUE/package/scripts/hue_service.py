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

from resource_management import *

def hue_service(
    name,
    searchingName,
    action = 'start'): 
    
    import params

    role = name
    processName = searchingName
    cmd = format("{hue_bindir}/hue")
    pid_file = format("{hue_piddir}/hue-{role}.pid")
    File(pid_file,
         action = "create",
         owner=params.hue_user
      )
    
    if action == 'start':
      daemon_cmd = format("{cmd} {role} &")
      Execute(daemon_cmd, user = params.hue_user)
      Execute('ps -ef | grep hue | grep ' + processName + ' | awk  \'{print $2}\' > ' + pid_file, user = params.hue_user)
      
    elif action == 'stop':
        
      Execute (format("cat {pid_file} | xargs kill -9"), user=params.hue_user, ignore_failures=True)

      File(pid_file,
           action = "delete",
           owner=params.hue_user
      )
