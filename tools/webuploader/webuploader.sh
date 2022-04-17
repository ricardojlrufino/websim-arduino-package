#!/bin/sh

echo "UPLOAD DONE.... java; $JAVA_HOME" 
FILE="$1"
APP="webuploader.jar"
ADDR="http://localhost:8887"

# Check if server is running

curl -sSf $ADDR > /dev/null
 
if [ $? -ne 22 ] ## (22) == 404 WebSocket Upgrade Failure
then
   echo "##### Starting Upload Server..."   
   java -jar $APP &
   sleep 10
fi

# echo send file info

java -jar $APP -f $FILE