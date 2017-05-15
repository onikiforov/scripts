#!/usr/local/bin/python

import re
import os
import sys
import subprocess

ssid = "<wifi_name>"
password = "<wifi_password>"
port = "<proxy_port>"
host = "<proxy_ip>"
current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
buildname = "proxy-setter-debug-0.2.apk"


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


def check_installed(i):
    output = execute_shell("adb shell pm list packages | grep 'proxysetter'", stdout=subprocess.PIPE)
    if not output:
        print("Installing app")
        execute_shell("adb -s %s install %s" % (i, current_dir + "/" + buildname))


def setup_proxy():
    execute_shell("adb shell am start -n tk.elevenk.proxysetter/.MainActivity -e host %s -e port %s -e ssid %s -e key %s"\
                % (host, port, ssid, password))


def clear_proxy():
    execute_shell("adb shell am start -n tk.elevenk.proxysetter/.MainActivity -e ssid %s -e key %s -e clear true" % \
                (ssid, password))


while True:
    try:
        raw_input("Attach device and press ENTER to continue or cmd+c to exit")

        # Run adb commands for each device

        output = execute_shell("adb devices", stdout=subprocess.PIPE)
        output = output.replace('List of devices attached\n', '').strip().split('\n')

        if output == ['']:
            print("No device found. Connect device and retry")
            sys.exit()

        for i in output:
            i = i.replace('\tdevice', '')
            # os.system("adb devices")
            print("")
            print("Device is %s" % i)

            if re.search("emulator-.*?", i):
                print("won't install on emulator")
            else:

                # Check that app is installed, install if not

                check_installed(i)

                # Prompt to setup proxy or clear

                print(30 * '-')
                print("Select action")
                print(30 * '-')
                print("1. Setup proxy")
                print("2. Clear proxy")
                print("3. Exit")
                print(30 * '-')

                choice = raw_input('Enter your choice [1-3] : ')

                choice = int(choice)

                if choice == 1:
                    setup_proxy()

                elif choice == 2:
                    clear_proxy()

                elif choice == 3:
                    print("Aborting...")
                    sys.exit()

                else:
                    print ("Invalid number. Try again...")
                    sys.exit()

    except KeyboardInterrupt:
        print("")
        print("Aborting script...")
        sys.exit()
