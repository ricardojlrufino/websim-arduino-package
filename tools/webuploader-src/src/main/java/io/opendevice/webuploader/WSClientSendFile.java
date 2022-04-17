package io.opendevice.webuploader;

import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft;
import org.java_websocket.drafts.Draft_6455;
import org.java_websocket.handshake.ServerHandshake;

public class WSClientSendFile {

  public static void send(final Path file) throws URISyntaxException, InterruptedException {

    Draft[] drafts = { new Draft_6455() };

    WebSocketClient client = new WebSocketClient(new URI("ws://localhost:" + Main.PORT), drafts[0]) {

      @Override
      public void onOpen(ServerHandshake handshakedata) {
        
        try {
          
          // Read file and send to WSServer ... to delivery to browser...
          byte[] bytes = Files.readAllBytes(file);
          this.send(bytes);
          
          System.out.print("[client] send ("+bytes.length+") : ");
          for (int i = 0; i < 40; i++) {
            System.out.print(bytes[i]);
            System.out.print(",");
          }
          System.out.println();
          
        } catch (IOException e) {
          e.printStackTrace();
          this.close();
        }
        
      }

      @Override
      public void onMessage(String message) {
        
        System.out.println("[client]:"+message);
        
        if(message.equals("/cmd/received")) {
          
        }
      }

      @Override
      public void onClose(int code, String reason, boolean remote) {
        System.out.println("[client]: closing ...");
      }

      @Override
      public void onError(Exception ex) {
        // TODO Auto-generated method stub
        
      }
      
    };
    
    boolean connected = client.connectBlocking();
    
    if(!connected) {
      System.err.println("Connection fail...");
    }else {
      Thread.sleep(1000);
      client.close();
    }

  }

}
