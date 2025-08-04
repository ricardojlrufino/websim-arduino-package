# Execute this after install package in Arduino IDE to speed-up local development
VERSION=1.2.0

echo "Setup links to this folder"

rm $HOME/.arduino15/package_websim_arduino_index_local.json
ln -s $PWD/package_websim_arduino_index_local.json $HOME/.arduino15/package_websim_arduino_index_local.json

# hardware
rm $HOME/.arduino15/packages/websim/hardware/avr/${VERSION}/platform.txt
rm $HOME/.arduino15/packages/websim/hardware/avr/${VERSION}/boards.txt

ln -s $PWD/websim-avr/platform.txt $HOME/.arduino15/packages/websim/hardware/avr/${VERSION}/platform.txt
ln -s $PWD/websim-avr/boards.txt $HOME/.arduino15/packages/websim/hardware/avr/${VERSION}/boards.txt

# tools webuploader
rm $HOME/.arduino15/packages/websim/tools/webuploader/1.2.0/webuploader-linux
ln -s $PWD/tools/webuploader-goport/bin/webuploader-linux $HOME/.arduino15/packages/websim/tools/webuploader/1.2.0/webuploader-linux

echo "Please Restart the IDE"

# Simulate a PACKAGE SERVER to arduino download the package
#cd ..
echo "Use http://localhost:3000/package_websim_arduino_index_local.json in Arduino IDE"
python3 -m http.server 3000
