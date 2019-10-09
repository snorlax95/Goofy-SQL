source fbsenv/bin/activate
cd ../app

pyinstaller --onefile --add-data="assets/*.png:assets" --add-data="views/*.ui:views" main.py

cd ../bin
