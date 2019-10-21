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
* export results table as xml/csv

* make columns expand better, right now everything is uniform but longer entries should be a bit bigger (min/max columns)

* Sort results table by column asc/desc (it's clickable, but since everything are strings..numbers are sorted incorrectly)

* Edit fields in results table (have listener to get row values, column name, and field value. Need to compare with table structure to make correct update statement)

* in ssh connect, allow user to select ssh key instead of password

* Structure View not finished

* in results table find way to use QSqlTableModel as it contains all the editing functionality we want out of the box (needs drivers intalled..would need to be included with app..commented out code is left in case we use it)
(only downside is it doesn't give us full control..leaving everything to qt and limiting to only 3 or 4 database types, also we have more control over styling)
