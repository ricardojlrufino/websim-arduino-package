#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

FILE="$1"
#APP="/media/ricardo/Dados/Workspace/Arduino/websim-arduino-package/tools/webuploader-src/target/webuploader-jar-with-dependencies.jar"
APP="${SCRIPT_DIR}/webuploader.jar"
echo "Uploading..."
java -jar $APP $FILE &

# wait for show serial on console...
sleep 4

# kill
# kill -9 $(ps xa | grep java | grep webuploader | awk '{print $1}')