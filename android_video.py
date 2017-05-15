#!/usr/local/bin/python

"""
get device name + ro.product.manufacturer, ro.product.brand
get time +
get app name+
combine into file name +
set bitrate (or don't)
start screen record : adb shell screenrecord /sdcard/demo.mp4 /
adb shell screenrecord --bit-rate 8000000 --time-limit 30 /sdcard/kitkat.mp4
wait for input to stop screen record
grab file from sdcard: adb pull /sdcard/demo.mp4
delete file on sdcard
"""

import re
import datetime
import os
import subprocess
import sys
import time

destination = '~/Downloads'


def execute_shell(command, working_directory=None, stdout=None, stderr=None):
    p = subprocess.Popen([command], cwd=working_directory, shell=True, stdout=stdout, stderr=stderr)
    if stderr:
        stdout, stderr = p.communicate()
        return stdout, stderr
    elif stdout:
        output = p.stdout.read()
        return output
    else:
        p.wait()


# Get device name: adb shell getprop ro.product.model
device_name = execute_shell('adb shell getprop ro.product.model', stdout=subprocess.PIPE).replace(" ", "-").strip()
if device_name == '':
    print("Please check that device is connected and restart the script")
    sys.exit(0)

device_version = execute_shell('adb shell getprop ro.build.version.release', stdout=subprocess.PIPE)\
    .replace(" ", "-").replace(".", "-").strip()

device_info = device_name + "_" + device_version

# Get current activity and grab package name from it: adb shell dumpsys window windows | grep -E 'mCurrentFocus'
activity_info = execute_shell("adb shell dumpsys window windows | grep -E 'mCurrentFocus'", stdout=subprocess.PIPE)

try:
    pattern = 'u0 (.*)\/.*\.(.*)}'
    app_name = re.search(pattern, activity_info).group(1).strip().replace(".", "-").replace(" ", "-")

except Exception:
    app_name = ""

# Get current time
now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Combine data in one string to use as screenshot name
screen_name = device_info + "_" + app_name + "_" + now + ".mp4"

# Start screen record

print("")
print("Press ctrl+c to stop recording")
print("")

cmdstring = "adb shell screenrecord --verbose /sdcard/%s" % screen_name
os.system(cmdstring)

# My guess is that interrupting video recording doesn't give system enough time to save file correctly
# without sleep it is corrupted
time.sleep(3)

execute_shell("adb pull /sdcard/%s %s" % (screen_name, destination))

execute_shell("adb shell rm /sdcard/%s" % screen_name)
