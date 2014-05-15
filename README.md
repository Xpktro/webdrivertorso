webdrivertorso.py - A humble homage to the Webdriver Torso Youtube Channel
==========================================================================

### Demo
https://www.youtube.com/watch?v=Vw3ST3p8t64

## Why?
For the sole prupose of entertainment.

## When?
I found the original channel in mid-april 2014, besides the conspiranoic nature of the channel, it's not so hard to replicate programatically.

## How?
`python webdrivertorso.py --help`

Also refer to the source code, you might find it interesting.


Install
=======
To successfully use this script you need (latest stable versions will do great):

 - **Python 2.7+ (with pip)**: Most GNU/Linux distributions comes with python. Installing pip would be as easy as `sudo apt-get install python-pip` (see your OS docs for details about package management). Windows users can download a Python installer from python.org and search the web for a pip installer. You'll also need the following python packages:
    - **Pillow:**  You'll need a C(++) compiler to build Pillow. Windows users can download a pre-compiled installer from the web.
    - **Gdata python API**
    - **youtube-upload**
    - ***To install these 3 dependencies:*** `(sudo) pip install -r requirements.txt`
 - **FFMPEG:** Grab the latest stable version from ffmpeg.org. GNU/Linux users might have and outdated version in their distro repositories so it's recommended to download the sources and build them. The official website haves a good and easy build guide.
 - **Courier New TTF font:** I cannot include it here because copyright issues. Grab the font from the web and copy `courbd.ttf` to this folder.

**Note (mostly for Windows users):** `ffmpeg` and `youtube-upload` must be in your system's PATH. (i.e. you can call them within the command line from anywhere)
