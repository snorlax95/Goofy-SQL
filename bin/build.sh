source fbsenv/bin/activate
cd ../app

pyinstaller --onefile --windowed --add-data="widgets/assets/*.png:widgets/assets" --add-data="widgets/views/*.ui:widgets/views" \
--icon="icon.ico" \
main.py

cd ../bin
