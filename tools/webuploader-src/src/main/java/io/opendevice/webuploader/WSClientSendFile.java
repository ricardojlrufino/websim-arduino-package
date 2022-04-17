package io.opendevice.webuploader;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft;
import org.java_websocket.drafts.Draft_6455;
import org.java_websocket.handshake.ServerHandshake;

public class WSClientSendFile {

  public static boolean send(final Path file) throws URISyntaxException, InterruptedException {

    Draft[] drafts = { new Draft_6455() };

    // Create client to previous started server..
    WebSocketClient client = new WebSocketClient(new URI("ws://localhost:" + Main.PORT), drafts[0]) {

      @Override
      public void onOpen(ServerHandshake handshakedata) {
        
        try {
          
          // Read file and send to WSServer ... to delivery to browser...
          byte[] bytes = Files.readAllBytes(file);
          
          // Print some bytes to Console...
          System.out.print("[client] hex bytes ("+bytes.length+") : ");
          for (int i = 0; i < 40; i++) {
            System.out.print(bytes[i]);
            System.out.print(",");
          }
          System.out.println();
          
          
          // Send File ...
          this.send(bytes);
      
        } catch (IOException e) {
          e.printStackTrace();
          this.close();
        }
        
      }

      @Override
      public void onMessage(String message) {
        
        System.out.println("[client]:received: "+message);
        
        if(message.equals("/cmd/received")) {
          
        }
      }

      @Override
      public void onClose(int code, String reason, boolean remote) {
        //System.out.println("[client]: closing ..." + code);
      }

      @Override
      public void onError(Exception ex) {
        // TODO Auto-generated method stub
      }
    };
    
    boolean connected = client.connectBlocking();
    
    if(connected) {
      // Wait for server close conection...
      while(client.isOpen()) {
        Thread.sleep(1000);
      }
      // client.close();
      return true;
    }else {
      //System.err.println("Connection fail...");
      return false;
    }

  }

}
