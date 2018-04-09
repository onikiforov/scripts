#!/usr/bin/python

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
import subprocess
import time
import os
import sys

destination = os.path.join(os.path.expanduser('~'), 'Documents/android_videos')


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


def get_device_data():
    device_data, error_data = execute_shell(
        'adb shell getprop | egrep "ro.product.model|ro.build.version.release"',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if error_data:
        print(error_data)
        sys.exit(0)
    device_name_pattern = '\[ro.product.model\]: \[(.*)\]'
    os_version_pattern = '\[ro.build.version.release\]: \[(.*)\]'
    device_name = re.search(device_name_pattern, device_data).group(1).replace(' ', '-').strip()
    print(device_name)
    os_version = re.search(os_version_pattern, device_data).group(1).replace(' ', '-').replace('.', '-').strip()
    print(os_version)

    return device_name, os_version


def get_app_name():
    activity_info = execute_shell('adb shell dumpsys window windows | grep "mCurrentFocus"', stdout=subprocess.PIPE)
    activity_info = activity_info.rstrip().lstrip()
    try:
        name_pattern = 'u\d (.*?)/.*\.(.*?)}$'
        app_name = re.search(name_pattern, activity_info).group(1).strip().replace('.', '-').replace(' ', '-')
        print(app_name)

    except AttributeError:
        app_name = ''

    return app_name


def main():
    # Get device name: adb shell getprop ro.product.model
    device_name, os_version = get_device_data()

    # Get current activity and grab package name from it: adb shell dumpsys window windows | grep 'mCurrentFocus'
    app_name = get_app_name()

    # Get current time
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Combine data in one string to use as screenshot name
    screen_name = '{}_{}_{}_{}.mp4'.format(device_name, os_version, app_name, now)

    print(screen_name)

    if not os.path.exists(destination):
        print('Folder for videos doesn\'t exist. Creating...')
        os.makedirs(destination)

    # Start screen record
    p = subprocess.Popen('adb shell screenrecord --verbose /sdcard/{}'.format(screen_name), shell=True)
    try:
        p.wait()
    except KeyboardInterrupt:
        p.kill()

    # My guess is that interrupting video recording doesn't give system enough time to save file correctly
    # - without sleep it is corrupted
    time.sleep(3)

    execute_shell('adb pull /sdcard/{} {}'.format(screen_name, destination))

    execute_shell('adb shell rm /sdcard/{}'.format(screen_name))


if __name__ == main():
    main()
