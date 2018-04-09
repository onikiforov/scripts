#!/usr/bin/python
import datetime
import os
import sys
import subprocess
import re
from PIL import Image


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


def get_ios_version(udid):
    try:
        ios_version_string = execute_shell('ideviceinfo -u {} | grep "ProductVersion"'.format(udid),
                                           stdout=subprocess.PIPE)
        ios_version = re.search('(\d+.*)$', ios_version_string).group().replace('.', '-')
    except Exception:
        ios_version = ''

    return ios_version


def main():
    # Select device to take screenshot from
    current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    config = current_dir + '/ios_devices.txt'
    screenshot_dest_folder = os.path.join(os.path.expanduser('~'), 'Documents/ios_screenshots')

    device_udids = execute_shell('idevice_id -l', stdout=subprocess.PIPE).strip('\n')

    if not device_udids:
        print('No device found, is it plugged in?')
        sys.exit(0)

    device_udids = device_udids.split('\n')

    all_devices = {}

    current_devices = {}

    try:
        with open(config, 'r') as f:
            for line in f:
                device_info = ([str(n) for n in line.strip().split('" ')])
                all_devices[device_info[0].replace('"', '')] = device_info[1]
    except IOError:
        f = open(config, 'w')
        f.close()

    for i in device_udids:
        for k, v in all_devices.items():
            if i == v:
                current_devices[k] = v

    for i in device_udids:
        if i not in current_devices.values():
            # We assume that device is not listed in our config and thus we need to add it
            print(30 * '-')
            try:
                device_name = execute_shell('idevicename -u {}'.format(i), stdout=subprocess.PIPE).rstrip('\n')
                if device_name == 'ERROR: Could not connect to device':
                    raise NameError
                print('We couldn\'t detect device in the list. It\'s name is {}'.format(device_name))
                print('Please enter device name and number(optional) in next format: 0186 iPhone 5S')
                print('OR')
                shall = raw_input('Should we use detected name? (y/N)\n').lower() == 'y'
                if not shall:
                    device_name = str(raw_input('Enter device name:\n'))
            except NameError:
                device_name = str(raw_input('Please enter device name and number(optional) in next format: '
                                            '0186 iPhone 5S'))
            current_devices[device_name] = i
            device_name = '"{}"'.format(device_name)
            print(device_name)
            device_info = '{} {}'.format(device_name, i)
            with open(config, 'a') as f:
                if not os.stat(config).st_size == 0:
                    f.write('\n')
                f.write(device_info)
            print(current_devices)

    if current_devices.__len__() == 1:
        name, udid = current_devices.items()[0]
        print(name)
        print(udid)

    else:
        print(30 * '-')
        print('   Select device')
        print(30 * '-')

        for item in enumerate(current_devices):
            print('[%d] %s' % item)

        try:
            print('')
            idx = int(raw_input('Enter number: '))
        except ValueError:
            print('Wrong number entered')
            sys.exit(0)

        try:
            name, udid = current_devices.items()[idx]
            print('')
            print('You chose {}'.format(name))
            print('')

        except IndexError:
            print('Try a number in range next time.')
            sys.exit(0)

    # Get iOS version
    ios_version = get_ios_version(udid)

    # Get current time
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Combine data in one string to use as screenshot name
    screen_name = (
        'ios_screenshot_{}_{}_{}'.format(name, ios_version, now)
    ).replace('.', '-').replace('=', '-').replace(' ', '-')

    if not os.path.exists(screenshot_dest_folder):
        print('Folder for screenshots doesn\'t exist. Creating...')
        os.makedirs(screenshot_dest_folder)

    # Make screenshot and save to specified location
    execute_shell(
        'idevicescreenshot -u {} {}/{}.tiff'.format(udid, screenshot_dest_folder, screen_name))

    # Convert screenshot from tiff to png to reduce size
    try:
        original_path = '{}/{}.tiff'.format(screenshot_dest_folder, screen_name)
        img = Image.open(original_path)
        converted_path = '{}/{}.png'.format(screenshot_dest_folder, screen_name)
        img.save(converted_path)

        # Delete tiff file
        os.remove(original_path)

    except IOError as e:
        print('\nScreenshot creation failed!\n')
        print(str(e))


if __name__ == main():
    main()
