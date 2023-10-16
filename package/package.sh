rm -rf build
rm -rf dist
rm __main__.spec
#https://github.com/pyinstaller/pyinstaller/issues/6381 不支持构建universal2，建议只使用x86_64
#--target-architecture x86_64 \


pyinstaller --onedir \
--osx-bundle-identifier com.karim.pymobile \
--name "pydevice" \
--clean \
--codesign-identity "Developer ID Application: Ye Kun Zhang (J3BJ7G2PUN)" \
--osx-entitlements-file ./pymobile.entitlements \
--add-data ../pymobiledevice3/resources/webinspector/*:pymobiledevice3/resources/webinspector/ \
--copy-metadata pyimg4 \
../pymobiledevice3/__main__.py
#codesign --force --verify --verbose=4 --sign "Developer ID Application: Ye Kun Zhang (J3BJ7G2PUN)" ./dist/__main__.app
# codesign --deep --force --options=runtime --entitlements ./pymobile.entitlements  --sign  "Developer ID Application: Ye Kun Zhang (J3BJ7G2PUN)" --timestamp ./dist/__main__.app
#pyinstaller -F --copy-metadata pyimg4 --add-data ../pymobiledevice3/resources/webinspector/*:resources/webinspector/ ../pymobiledevice3/__main__.py
# rm -rf /Users/karimzhang/home/project/Magellan/MacDeviceControl/lib/pydevice.bundle/
# cp -r dist/pydevice /Users/karimzhang/home/project/Magellan/MacDeviceControl/lib/pydevice.bundle/