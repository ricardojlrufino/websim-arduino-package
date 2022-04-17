#!/bin/sh

FILE="$1"
APP="/media/ricardo/Dados/Workspace/Arduino/websim-arduino-package/tools/webuploader-src/target/webuploader-jar-with-dependencies.jar"
echo "Uploading..."
java -jar $APP $FILE &

# wait for show serial on console...
sleep 4