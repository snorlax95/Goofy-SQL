source fbsenv/bin/activate
cd ../app

pyinstaller --onefile --windowed --add-data="assets/*.png:assets" --add-data="views/*.ui:views" \
--icon="icon.ico" \
main.py

cd ../bin
