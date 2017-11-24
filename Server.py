import socket
from Queue import Queue
from threading import Thread
from threading import Lock
import re as regex
import hashlib
import os
import sys

p = 0
h = ""
chatUsers = Queue()

arr = {}

loc = Lock()


class CR:
    def __init__(self, r_name, r_id):

        self.r_name = r_name
        self.r_id = r_id
        self.r_users = {}
        self.r_lock = Lock()

    def add_usr(self, con, p, h, u_id, u_name):
        self.r_lock.acquire()
        try:
            self.r_users[u_id] = (u_name, con)
        finally:
            self.r_lock.release()
        return "JOINED_CHATROOM: " + self.r_name + "\nSERVER_IP: " + str(h) + "\nPORT: " + str(
            p) + "\nROOM_REF: " + str(self.r_id) + "\nJOIN_ID: " + str(u_id)

    def send_usr_message(self, u, m):
        u_conns = []
        self.r_lock.acquire()
        try:
            u_conns = self.r_users.values()
        finally:
            self.r_lock.release()
        for dest_user, dest_conn in u_conns:
            msg_client("CHAT:" + str(self.r_id) + "\nCLIENT_NAME:" + str(u) + "\nMESSAGE:" + m + "\n",
                       dest_conn)

    def remove_usr(self, u_id, u_name, con):
        self.r_lock.acquire()
        try:
            if u_id in self.r_users:
                if self.r_users[u_id][0] == u_name:
                    del self.r_users[u_id]
                else:
                    return
        finally:
            self.r_lock.release()

    def disconnect_cr(self, u_id, u_name, con):
        self.r_lock.acquire()
        try:
            if u_id not in self.r_users:
                return
        finally:
            self.r_lock.release()
        self.send_usr_message(u_name, u_name + " has left this chatroom.")
        self.r_lock.acquire()
        try:
            del self.r_users[u_id]
        finally:
            self.r_lock.release()


def dis_usr(con, u_name):
    u_id = str(int(hashlib.md5(u_name).hexdigest(), 16))
    rooms = []
    loc.acquire()
    try:
        rooms = arr.values()
    finally:
        loc.release()
    rooms = sorted(rooms, key=lambda x: x.r_name)
    for r in rooms:
        r.disconnect_cr(u_id, u_name, con)


def send_msg_to_all_usr(con, r_id, u_id, u_name, msg):
    room = None
    loc.acquire()
    try:
        if r_id not in arr:
            err_client("Wrong Format", 9, con)
            return
        room = arr[r_id]
    finally:
        loc.release()
    room.send_usr_message(u_name, msg)


def create_cr(con, r_name, u_name):
    r_id = str(int(hashlib.md5(r_name).hexdigest(), 16))
    u_id = str(int(hashlib.md5(u_name).hexdigest(), 16))
    loc.acquire()
    try:
        if r_id not in arr:
            arr[r_id] = CR(r_name, r_id)
        room = arr[r_id]
    finally:
        loc.release()

    msg_client(room.add_usr(con, p, h, u_id, u_name), con)
    room.send_usr_message(u_name, u_name + "has joined the chat room")


def del_user(con, r_id, u_id, u_name):
    room = None
    loc.acquire()
    try:
        if r_id not in arr:
            err_client("Room not found", 1, con)
            return
        room = arr[r_id]
    finally:
        loc.release()
    msg_client("LEFT_CHATROOM: " + str(r_id) + "\nJOIN_ID: " + str(u_id), con)
    room.send_usr_message(u_name, u_name + " has left this chatroom.")
    room.remove_usr(u_id, u_name, con)


def err_client(err_desc, err_code, con):
    message = "ERROR_CODE: " + str(err_code) + "\nERROR_DESCRIPTION: " + err_desc
    msg_client(message, con)


def msg_client(message, con):
    if con:
        con.sendall((message + "\n").encode())


class ChatUsersThreadClass(Thread):
    def __init__(self, chatUsers):
        Thread.__init__(self)
        self.chatUsers = chatUsers
        self.start()

    def run(self):
        while True:
            (con, addr) = self.chatUsers.get()
            if con:
                self.check_msg(con, addr)
            else:
                break

    @staticmethod
    def check_msg(con, addr):

        while con:
            m = ""
            while "\n\n" not in m:
                message_content = con.recv(1024)
                m += message_content.decode()
                if len(message_content) < 1024:
                    break

            if len(m) > 0:

                if m == "KILL_SERVICE\n":
                    os._exit(0)

                if m.startswith("HELO"):
                    m_components = regex.match(r"HELO ?(.*)\s", m, regex.M)
                    if m_components is not None:
                        msg_client("HELO " + m_components.groups()[0] + "\nIP:" + str(h) + "\nPort:" + str(
                            p) + "\nStudentID:" + "17311875", con)
                    else:
                        err_client("Wrong Format", 9, con)

                if m.startswith("JOIN_CHATROOM"):
                    m_components = regex.match(
                        r"JOIN_CHATROOM: ?(.*)(?:\s|\\n)CLIENT_IP: ?(.*)(?:\s|\\n)PORT: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)",
                        m, regex.M)
                    if m_components is not None:
                        create_cr(con, m_components.groups()[0], m_components.groups()[3])
                    else:
                        err_client("Wrong Format", 9, con)

                if m.startswith("LEAVE_CHATROOM"):
                    m_components = regex.match(
                        r"LEAVE_CHATROOM: ?(.*)(?:\s|\\n)JOIN_ID: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)", m, regex.M)
                    if m_components is not None:
                        del_user(con, m_components.groups()[0], m_components.groups()[1], m_components.groups()[2])
                    else:
                        err_client("Wrong Format", 9, con)

                if m.startswith("CHAT"):
                    m_components = regex.match(
                        r"CHAT: ?(.*)(?:\s|\\n)JOIN_ID: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)(?:\s|\\n)MESSAGE: ?(.*)", m,
                        regex.M)
                    if m_components is not None:
                        send_msg_to_all_usr(con, m_components.groups()[0], m_components.groups()[1],
                                            m_components.groups()[2], m_components.groups()[3])
                    else:
                        err_client("Wrong Format", 9, con)

                if m.startswith("DISCONNECT"):
                    m_components = regex.match(r"DISCONNECT: ?(.*)(?:\s|\\n)PORT: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)", m,
                                               regex.M)
                    if m_components is not None:
                        dis_usr(con, m_components.groups()[2])
                    else:
                        err_client("Wrong Format", 9, con)
                    con.shutdown(1)
                    con.close()
                    break


def main():
    global p, h

    print ("Initializing server")

    if len(sys.argv) != 2:
        sys.exit("Port Number not specified")

    p = int(sys.argv[1])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    h = socket.gethostbyname(socket.gethostname())
    sock.bind((h, p))
    sock.listen(8)
    while True:
        con, addr = sock.accept()
        ChatUsersThreadClass(chatUsers)
        chatUsers.put((con, addr))


if __name__ == '__main__':
    main()
