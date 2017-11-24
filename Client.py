import socket
import hashlib
import sys


def client():

    if len(sys.argv) < 2:
        sys.exit("Port not specified")

    p = int(sys.argv[1])

    h = socket.gethostbyname(socket.gethostname())
    s = socket.socket()
    s.connect((h, p))
    s.send("HELO " + "c" + "\n".encode())
    r_msg = s.recv(1024).decode()
    print('Msg:\n' + r_msg)
    s.send("JOIN_CHATROOM: " + "r" + "\nCLIENT_IP: 0\nPORT: 0\nCLIENT_NAME: " + "c".encode())
    r_msg = s.recv(1024).decode()
    print('Msg:\n' + r_msg)
    s.send("CHAT: " + str(int(hashlib.md5("r").hexdigest(), 16)) + "\nJOIN_ID: " + str(
        int(hashlib.md5("c").hexdigest(), 16)) + "\nCLIENT_NAME: " + "c" + "\nMESSAGE: " + "m".encode())
    r_msg = s.recv(1024).decode()
    print('Msg:\n' + r_msg)
    s.send("LEAVE_CHATROOM: " + str(int(hashlib.md5("r").hexdigest(), 16)) + "\nJOIN_ID: " + str(
        int(hashlib.md5("c").hexdigest(), 16)) + "\nCLIENT_NAME: " + "c".encode())
    r_msg = s.recv(1024).decode()
    print('Msg:\n' + r_msg)
    s.send("DISCONNECT: 0\nPORT: 0\nCLIENT_NAME: " + "c".encode())
    r_msg = s.recv(1024).decode()
    print('Msg:\n' + r_msg)
    s.close()

if __name__ == '__main__':
    client()
