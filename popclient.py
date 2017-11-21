"""
    Класс-клиент протокола POP
"""


from socket import socket


class PopClient():

    HOST    = "mail.edm-core.ru"
    PORT    = 110
    TIMEOUT = 60
    MSG_LEN = 1024


    def __init__(self, login, pwd):
        self.is_authorized = False
        self.login = login
        self.pwd = pwd
        self.socket = socket()
        self.socket.settimeout(self.TIMEOUT)
        self.connect()


    def __del__(self):
        self.quit()
        self.socket.close()


    def read(self):
        return self.parse(self.socket.recv(self.MSG_LEN))


    def parse(self, message):
        message = message.decode("utf-8")
        title, *body = message.split("\n")
        status, *caption = title.split(" ")
        body = [line.strip() for line in body]
        caption = " ".join(caption).strip()
        status = status.strip()
        return {
            "status"  : "+" if status.lower() == "+ok" else "-",
            "caption" : caption
        }


    def authorize(self, login, pwd):
        self.is_ok(self.user(login), "Не удалось авторизоваться !")
        self.is_ok(self.pasw(pwd), "Не удалось авторизоваться !")
        self.is_authorized = True


    def is_ok(self, response, error_message):
        if response["status"] == "-":
            raise Exception(error_message)


    def send(self, cmd, params={}):
        self.check()
        if cmd == "stat":
            response = self.stat()
        elif cmd == "list":
            response = self.list(params["msg_num"])
        elif cmd == "top":
            response = self.top(params["msg_num"], params["line_count"])
        elif cmd == "rset":
            response = self.rset()
        elif cmd == "dele":
            response = self.dele(params["msg_num"])
        elif cmd == "retr":
            response = self.retr(params["msg_num"])
        else:
            raise Exception("Несуществующая команда '{0}'".format(cmd))
        self.is_ok(response, "Ошибка при отправке команды !")
        if "status" in response:
            response.pop("status")
        return response


    def connect(self):
        self.socket.connect((self.HOST, self.PORT))
        self.is_ok(self.read(), "Не удалось соединиться с POP-сервером !")
        self.authorize(self.login, self.pwd)


    def check(self):
        if self.is_authorized == True:
            response = self.noop()
            if response["status"] == "-":
                self.connect()


    def user(self, name):
        self.socket.send("USER {0}\n".format(name).encode("utf-8"))
        return self.read()


    def pasw(self, pwd):
        self.socket.send("PASS {0}\n".format(pwd).encode("utf-8"))
        return self.read()


    def quit(self):
        self.socket.send(b"QUIT\n")
        return self.read()


    def stat(self):
        self.socket.send(b"STAT\n")
        # OK number number
        status, msg_count, general_size = self.socket.recv(self.MSG_LEN).decode("utf-8").split(" ")
        return {
            "status"       : "+" if status.lower() == "+ok" else "-",
            "msg_count"    : msg_count.strip(),
            "general_size" : general_size.strip()
        }


    def list(self, msg_num):
        msg = "LIST\n" if msg_num is None else "LIST {0}\n".format(msg_num)
        self.socket.send(msg.encode("utf-8"))
        # +OK number number
        #
        # +OK number messages:
        # number number
        # number number
        # .
        if msg_num is None:
            title, *body = self.socket.recv(self.MSG_LEN).decode("utf-8").split("\n")
            status, msg_count, other = title.split(" ")
            msg_count = int(msg_count)
            lines = []
            for i in range(msg_count):
                msg_num, msg_size = body[i].split(" ")
                lines.append({
                    "msg_num"  : int(msg_num),
                    "msg_size" : int(msg_size)
                })
            return {
                "status"    : "+" if status.lower() == "+ok" else "-",
                "msg_count" : msg_count,
                "body"      : lines
            }
        else:
            status, *other = self.socket.recv(self.MSG_LEN).decode("utf-8").split(" ")
            self.is_ok({
                "status" : "+" if status.lower() == "+ok" else "-"
            }, "Сообщения с номером '{0}' не существует !".format(msg_num))
            msg_num, msg_size = other
            return {
                "status"   : "+",
                "msg_size" : int(msg_size)
            }


    def retr(self, msg_num):
        self.socket.send("RETR {0}\r\n".format(msg_num).encode("utf-8"))
        # +OK number octets
        # text text text
        # Subject:title
        #
        # line 1
        # line 2
        # line 3
        # .
        title, *body = self.socket.recv(self.MSG_LEN).decode("utf-8").split("\n")
        status, *other = title.split(" ")
        self.is_ok({
            "status" : "+" if status.lower() == "+ok" else "-"
        }, "Сообщения с номером '{0}' не существует !".format(msg_num))
        msg_size = int(other[0])
        is_read = False
        text = []
        for line in body:
            line = line.strip()
            if "Subject" in line:
                title = line.split(":")[1]
            elif line is "":
                is_read = True
            elif line is ".":
                is_read = False
            elif is_read:
                text.append(line.strip())
        return {
            "status"   : "+",
            "msg_size" : msg_size,
            "title"    : title.strip(),
            "body"     : "\n".join(text)
        }


    def top(self, msg_num, line_count):
        self.socket.send("TOP {0} {1}\r\n".format(msg_num, line_count).encode("utf-8"))
        # +OK number octets
        # text text text
        # Subject:title
        #
        # line 1
        # line 2
        # line 3
        # .
        status, *body = self.socket.recv(self.MSG_LEN).decode("utf-8").split("\n")
        self.is_ok({
            "status" : "+" if status.strip().lower() == "+ok" else "-"
        }, "Сообщения с номером '{0}' не существует !".format(msg_num))
        is_read = False
        text = []
        for line in body:
            line = line.strip()
            if "Subject" in line:
                title = line.split(":")[1]
            elif line is "":
                is_read = True
            elif line is ".":
                is_read = False
            elif is_read:
                text.append(line.strip())
        return {
            "status"   : "+",
            "title"    : title.strip(),
            "body"     : "\n".join(text)
        }


    def dele(self, msg_num):
        self.socket.send("DELE {0}\n".format(msg_num).encode("utf-8"))
        return { "status" : self.read()["status"]}


    def rset(self):
        self.socket.send(b"RSET\n")
        return { "status" : self.read()["status"]}


    def noop(self):
        self.socket.send(b"NOOP\n")
        return { "status" : self.read()["status"]}
