# Crossplatform SQL GUI

Currently there are no great applications for windows, this project
will provide an easy to use, consistent UI for bot mac and windows


## requirements
1. python 3.7.2


## mac/windows
if on mac, it will use Macintosh style set in application.py
if on windows/linux it will use Fusion style


## run locally
cd into bin
command: . run.sh


# build
install pyinstaller
cd into app
pyinstaller main.spec

(build should then be available in dist folder, main.exe)