rm -rf build
rm -rf dist
rm __main__.spec
#--target-architecture universal2
pyinstaller -w --onedir --osx-bundle-identifier com.karim.pymobile --exclude-module IPython --codesign-identity "Developer ID Application: Ye Kun Zhang (J3BJ7G2PUN)" --osx-entitlements-file ./pymobile.entitlements --copy-metadata pyimg4 --add-data ../pymobiledevice3/resources/webinspector/*:resources/webinspector/ ../pymobiledevice3/__main__.py
#codesign --force --verify --verbose=4 --sign "Developer ID Application: Ye Kun Zhang (J3BJ7G2PUN)" ./dist/__main__.app
# codesign --deep --force --options=runtime --entitlements ./pymobile.entitlements  --sign  "Developer ID Application: Ye Kun Zhang (J3BJ7G2PUN)" --timestamp ./dist/__main__.app
#pyinstaller -F --copy-metadata pyimg4 --add-data ../pymobiledevice3/resources/webinspector/*:resources/webinspector/ ../pymobiledevice3/__main__.py
# rm -rf /Users/karimzhang/home/project/Magellan/MacDeviceControl/lib/pymobiledevice3.bundle/__main__
# cp -r dist/__main__ /Users/karimzhang/home/project/Magellan/MacDeviceControl/lib/pymobiledevice3.bundle/