 
#!/bin/sh
VERSION=0.1.2

zip -r websim-avr-${VERSION}.zip websim-avr
python package_update_json.py package_websim_arduino_index_local.json --platform "WebSim AVR Boards" --from-file websim-avr-${VERSION}.zip
python package_update_json.py package_websim_arduino_index.json --platform "WebSim AVR Boards" --from-file websim-avr-${VERSION}.zip

# Build tools
echo "Building tools..."

# webuploader
cd ./tools/webuploader-v2
make dist

#ls -la *.gz
#cd ..
#ls -la *.zip