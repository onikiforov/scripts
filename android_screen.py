#!/usr/local/bin/python

"""
get device name: adb shell getprop ro.product.model +
get activity adb shell dumpsys window windows | grep -E 'mCurrentFocus' +
get time +
combine +
use as screen name adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > screen.png +
"""

import re
import datetime
import sys
import time
import subprocess

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

# What if we want to take screenshot of lock screen? No application or activity

pattern = 'u0 (.*)\/.*\.(.*)}'

try:
    app_name = re.search(pattern, activity_info).group(1).strip().replace(".", "-").replace(" ", "-")
except Exception:
    app_name = ""

try:
    activity_name = re.search(pattern, activity_info).group(2).strip().replace(".", "-").replace("=", "-").replace(" ",
                                                                                                                   "-")
except Exception:
    activity_name = ""

activity_name = app_name + "_" + activity_name

# Get current time 
now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Combine data in one string to use as screenshot name
screen_name = device_info + "_" + activity_name + "_" + now + ".png"

# Take screenshot, grab it from device to the destination and delete file on device; Sleep is used to process files

print("taking screenshot")

execute_shell("adb shell screencap -p /sdcard/screen.png")
time.sleep(1)
execute_shell("adb pull /sdcard/screen.png %s/%s" % (destination, screen_name))
time.sleep(1)
execute_shell("adb shell rm /sdcard/screen.png")
