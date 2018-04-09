## Repo to store custom scripts used in testing

## Currently contains next scripts:

- android_screen.py - script to take a screenshot from connected Android device and save it locally
- android_video.py - script to take a video from connected Android device and save it locally. Works on versions > 4.4
- android_proxy.py - script to setup/remove proxy on connected Android device. Works on versions < 6.0
- ios_video.py - script to take a screenshot from connected iOS device and save it locally (OS X only)

To use scripts:
1. Download script file
2. `Cd` to folder with script and `python <script_name>.py`

OR

2. `chmod +x <script_name>.py`
3. Add to PATH
4. `<script_name>.py`

Scripts were tested only on OS X environment

### android_screen.py
Specify destination folder ("~/Documents/android_screenshots" by default)

Connect device

Run script

### android_video.py
Specify destination folder ("~/Documents/android_videos" by default)

Connect device

Run script

ctrl+c to interrupt recording (record a few seconds more, as result file may be trimmed)

### ios_screen.py
Specify destination folder ("~/Documents/ios_screenshots" by default)

Connect device

Run script

If run for first time with a device > will ask to specify device name. Names with udids are stored in "ios_devices.txt" in same folder as script

### Dependencies:
ios.py requires:
* "PIL" for image rotation: `pip install http://effbot.org/media/downloads/Imaging-1.1.7.tar.gz`
* "libimobiledevice" for connection with device:
  * `brew install libimobiledevice`
OR 
  * `brew install https://gist.github.com/Haraguroicha/0dee2ee29c7376999178c5392080c16e/raw/libimobiledevice.rb --HEAD --with-ios11`
OR
  * Download from https://github.com/libimobiledevice/libimobiledevice and build locally
