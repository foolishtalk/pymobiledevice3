rm -rf build
rm -rf dist
rm __main__.spec
pyinstaller -D --copy-metadata pyimg4 --add-data ../pymobiledevice3/resources/webinspector/*:resources/webinspector/ ../pymobiledevice3/__main__.py
rm -rf /Users/karimzhang/home/project/Magellan/MacDeviceControl/lib/pymobiledevice3.bundle/__main__
cp -r dist/__main__ /Users/karimzhang/home/project/Magellan/MacDeviceControl/lib/pymobiledevice3.bundle/