#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
FILE="$1"
webuploader-linux $1

# wait for show serial on console...
sleep 4

# kill
# kill -9 $(ps xa | grep java | grep webuploader | awk '{print $1}')