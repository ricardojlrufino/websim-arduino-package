package io.opendevice.webuploader;

import java.net.URISyntaxException;
import java.net.UnknownHostException;
import java.nio.file.Paths;
import java.util.Arrays;

public class Main {
  
  public static final int PORT = 8887; 
  
  public static void main(String[] args) throws UnknownHostException, URISyntaxException, InterruptedException {
    
    System.out.println("[java]" + Arrays.asList(args));
    
    if(args.length > 1) { // Start as Client
      
      System.out.println("[java]" + "Send to client");
    
      WSClientSendFile.send(Paths.get(args[1]));
      
    }else {
      
      WSServer s = new WSServer(PORT);
      s.run();
  
    }
    
  }

}
