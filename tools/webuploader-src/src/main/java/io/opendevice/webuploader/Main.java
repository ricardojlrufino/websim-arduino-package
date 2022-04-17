package io.opendevice.webuploader;

import java.net.URISyntaxException;
import java.net.UnknownHostException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;

public class Main {
  
  public static final int PORT = 8887; 
  
  public static void main(String[] args) throws UnknownHostException, URISyntaxException, InterruptedException {
    
    final Path hexFile = Paths.get(args[0]);
    
    if(!Files.exists(hexFile)) {
      System.out.println("invalid file : " + hexFile);
      System.exit(-1);
    }
    
    boolean sended = WSClientSendFile.send(hexFile);
    
    // Start if server  is not running
    if(!sended) {
      
      System.out.println("[uploader] starting server...");
      System.out.println("[uploader] Open: https://websim-arduino.web.app");
      System.out.println("####### PLEASE RUN UPLOAD AGAIN !! #######");
      WSServer s = new WSServer(PORT);
      s.run(); // run in foregroud.
      
    }
    
    
  }

}
