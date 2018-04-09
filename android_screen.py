#!/usr/bin/python

"""
get device name: adb shell getprop ro.product.model +
get activity adb shell dumpsys window windows | grep 'mCurrentFocus' +
get time +
combine +
use as screen name adb shell screencap -p | perl -pe 's/\x0D\x0A/\x0A/g' > screen.png +
"""

import re
import datetime
import os
import time
import subprocess
import sys

should_rotate = True
os.path.expanduser('~')
destination = os.path.join(os.path.expanduser('~'), 'Documents/android_screenshots')

"""
TODO: check device status with "adb get-state", do not execute with the help of "adb wait-for-device"
"""


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


def get_activity_name():
    activity_info = execute_shell('adb shell dumpsys window windows | grep "mCurrentFocus"', stdout=subprocess.PIPE)
    activity_info = activity_info.rstrip().lstrip()
    print(activity_info)

    # What if we want to take screenshot of lock screen? No application or activity
    try:
        name_pattern = 'u\d (.*?)/.*\.(.*?)}$'
        app_name = re.search(name_pattern, activity_info).group(1).strip().replace('.', '-').replace(' ', '-')
        activity_name = re.search(name_pattern, activity_info).group(2).strip() \
            .replace('.', '-').replace('=', '-').replace(' ', '-')
        print(app_name)
        print (activity_name)

    except AttributeError:
        app_name = ''
        activity_name = ''
    activity_name = app_name + '_' + activity_name

    return activity_name


def get_device_orientation():
    device_orientation = execute_shell(
        'adb shell dumpsys input | grep \'SurfaceOrientation\' | awk \'{ print $2 }\'',
        stdout=subprocess.PIPE
    )
    print('device_orientation: {}'.format(device_orientation))
    return device_orientation


def rotate_screenshot(device_orientation, screen_name, dst):
    try:
        image_size = execute_shell('identify -format \'%w %h\' {}/{}'.format(dst, screen_name),
                                   stdout=subprocess.PIPE)
        image_width, image_height = re.search('(\d+) (\d+)', image_size).groups()

        if int(device_orientation) in (1, 3) and int(image_height) > int(image_width):
            print('Device is in landscape and image is in portrait\nRotating...')
            if int(device_orientation) == 1:
                execute_shell(
                    'convert -rotate 270 {}/{} {}/{}'.format(dst, screen_name, dst, screen_name)
                )
            else:
                execute_shell(
                    'convert -rotate 90 {}/{} {}/{}'.format(dst, screen_name, dst, screen_name)
                )

    except Exception:
        print(Exception.message)


def main():
    # Get device name and os version: adb shell getprop | egrep "ro.product.model|ro.build.version.release"
    device_name, os_version = get_device_data()

    # Get current activity and grab package name from it: adb shell dumpsys window windows | grep 'mCurrentFocus'
    activity_name = get_activity_name()

    # Get device orientation
    device_orientation = get_device_orientation()

    # Get current time
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Combine data in one string to use as screenshot name
    screen_name = '{}_{}_{}_{}.png'.format(device_name, os_version, activity_name, now)

    if not os.path.exists(destination):
        print('Folder for screenshots doesn\'t exist. Creating...')
        os.makedirs(destination)

    # Take screenshot, grab it from device to the destination and delete file on device

    print('Taking screenshot...')

    execute_shell('adb shell screencap -p /sdcard/screen.png')
    time.sleep(1)
    execute_shell('adb pull /sdcard/screen.png {}/{}'.format(destination, screen_name))
    time.sleep(1)
    execute_shell('adb shell rm /sdcard/screen.png')

    if should_rotate:
        rotate_screenshot(device_orientation, screen_name, destination)


if __name__ == main():
    main()
