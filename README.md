# Chat Server Application

This chat server Application can support multiple clients where clients can join chat rooms, post messages and retrieve messages, and leave chat rooms.

Dependency -->  Python 2.7

# process 

* Starting the Server
* Testing of the Server from the test client

# Welcome Msg to Server
Request
     
     "HELO text\n"

# Join Msg to Server
Request

     JOIN_CHATROOM: [chatroom name]
     CLIENT_IP: [IP Address of client if UDP | 0 if TCP]
     PORT: [port number of client if UDP | 0 if TCP]
     LIENT_NAME: [string Handle to identifier client user]
     
# Leave Msg to Server
Request

     LEAVE_CHATROOM: [ROOM_REF]
     JOIN_ID: [integer previously provided by server on join]
     CLIENT_NAME: [string Handle to identifier client user]
     
# Chat Msg to Server
Request

    CHAT: [ROOM_REF]
    JOIN_ID: [integer identifying client to server]
    CLIENT_NAME: [string identifying client user]
    MESSAGE: [string terminated with '\n\n']
    
# Dissconnect Msg to Server
Request

     DISCONNECT: [IP address of client if UDP | 0 if TCP]
     PORT: [port number of client it UDP | 0 id TCP]
     CLIENT_NAME: [string handle to identify client user]

