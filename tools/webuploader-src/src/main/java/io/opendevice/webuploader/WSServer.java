package io.opendevice.webuploader;

import java.net.InetSocketAddress;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.util.Collections;

import org.java_websocket.WebSocket;
import org.java_websocket.drafts.Draft;
import org.java_websocket.drafts.Draft_6455;
import org.java_websocket.handshake.ClientHandshake;
import org.java_websocket.server.WebSocketServer;


public class WSServer extends WebSocketServer {
  
  public static final String WEB_SIGNATURE = "{\"from\":\"web\"";

  public static WebSocket webClient;

  public WSServer(int port) throws UnknownHostException {
    super(new InetSocketAddress(port));
  }

  public WSServer(InetSocketAddress address) {
    super(address);
  }

  public WSServer(int port, Draft_6455 draft) {
    super(new InetSocketAddress(port), Collections.<Draft>singletonList(draft));
  }

  @Override
  public void onOpen(WebSocket conn, ClientHandshake handshake) {
    
    conn.send("Welcome to the WebSIM server!"); //This method sends a message to the new client
    
    System.out.println("[server]" +conn.getRemoteSocketAddress().getAddress().getHostAddress() + " entered the room!");
  }

  @Override
  public void onClose(WebSocket conn, int code, String reason, boolean remote) {
    broadcast(conn + " has left the room!");
    System.out.println(conn + " has left the room!");
  }

  @Override
  public void onMessage(WebSocket conn, String message) {
    broadcast(message);
    System.out.println(conn + ": " + message);
    
    if(message.contains(WEB_SIGNATURE)) {
      WSServer.webClient = conn;
    }
    
  }

  @Override
  public void onMessage(WebSocket conn, ByteBuffer message) {
    
    // Send to web-browser...
    if(WSServer.webClient != null && WSServer.webClient.isOpen()) {
      WSServer.webClient.send(message);
    }else { // try to send to all clients...
      broadcast(message);  
    }
    
    System.out.println("[server] " + conn + ": Binary message" + message);
    
    conn.close(); // force client close...
  }

  @Override
  public void onError(WebSocket conn, Exception ex) {
    ex.printStackTrace();
    if (conn != null) {
      // some errors like port binding failed may not be assignable to a specific websocket
    }
  }

  @Override
  public void onStart() {
    System.out.println("Server started on port :" + this.getPort());
    setConnectionLostTimeout(0);
    setConnectionLostTimeout(100);
    
    // Clean shuwdown...
    Runtime.getRuntime().addShutdownHook(new Thread() {
      @Override
      public void run() {
        try {
          WSServer.this.stop();
        } catch (InterruptedException e) {
          e.printStackTrace();
        }
      }
    });

  }
  

}