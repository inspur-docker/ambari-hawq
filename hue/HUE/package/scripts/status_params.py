#!/usr/bin/env python
from resource_management import *

# config object that holds the status related configurations declared in the -env.xml file
config = Script.get_config()

hue_piddir = config['configurations']['hue-env']['hue_pid_dir']
hue_port = config['configurations']['hue-env']['hue.port']
hue_pidfile = format("{hue_piddir}/hue-{hue_port}.pid")