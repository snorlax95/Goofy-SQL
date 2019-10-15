# Crossplatform SQL GUI

Currently there are no great applications for windows, this project
will provide an easy to use, consistent UI for both mac and windows


## requirements
1. python 3.7.2
2. pyinstaller (for builds)


## mac/windows
if on mac, it will use Macintosh style set in application.py
if on windows/linux it will use Fusion style


## run locally
cd into bin
command: . run.sh


# build
cd into bin
command: . build.sh

(build should then be available in dist folder, main.exe or main.app)


# Features needed

* ContentView (Refresh isn’t getting the correct results when new rows are available)

* export results table as xml/csv

* make columns expand better, right now everything is uniform but longer entries should be a bit bigger (min/max columns)

* style table items by type..color coded if possible. Strings, Integer, NULL, and datetimes could be styled different

* Sort results table by column asc/desc (it's clickable, but since everything are strings..numbers are sorted incorrectly)

* Edit fields in results table
