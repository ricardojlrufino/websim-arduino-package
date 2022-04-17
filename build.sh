 
#!/bin/sh


zip -r websim-avr-1.0.zip websim-avr

cd tools
cp webuploader-src/target/webuploader-jar-with-dependencies.jar webuploader/webuploader.jar
#zip -r webuploader-1.0.0.zip webuploader
tar -czvf webuploader-1.0.0.tar.gz webuploader

ls -la *.gz
cd ..
ls -la *.zip