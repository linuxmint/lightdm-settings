#!/usr/bin/python3

import os
import subprocess
import sys

if os.getuid() != 0:
    print("lightdm-settings needs to be run as root.")
    sys.exit(1)

subprocess.Popen("/usr/lib/lightdm-settings/lightdm-settings")
