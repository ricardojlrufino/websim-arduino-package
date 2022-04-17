 
#!/bin/sh


zip -r websim-avr-1.0.zip websim-avr

cd tools
cp webuploader-src/target/webuploader-jar-with-dependencies.jar webuploader/webuploader.jar
zip -r webuploader-1.0.0.zip webuploader

ls -la *.zip
cd ..
ls -la *.zip