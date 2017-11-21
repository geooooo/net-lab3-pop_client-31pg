from popclient import PopClient


try:
    client = PopClient("test@edm-core.ru", "123qwerty123")

    while True:
        print("Введите команду: ", end="")
        cmd = input().strip()
        if cmd == "stat":
            response = client.send("stat")
            print(response)
        elif cmd == "list":
            print("Введите номер сообщения (необязательно): ", end="")
            msg_num = input().strip()
            response = client.send("list", {
                "msg_num" : None if msg_num == "" else msg_num
            })
            print(response)
        elif cmd == "retr":
            print("Введите номер сообщения: ", end="")
            msg_num = input().strip()
            response = client.send("retr", {
                "msg_num" : msg_num
            })
            print(response)
        elif cmd == "dele":
            print("Введите номер сообщения: ", end="")
            msg_num = input().strip()
            client.send("dele", {
                "msg_num" : msg_num
            })
        elif cmd == "rset":
            client.send("rset", {
                "msg_num" : msg_num
            })
        elif cmd == "top":
            print("Введите номер сообщения: ", end="")
            msg_num = input().strip()
            print("Введите количество строк: ", end="")
            line_count = input().strip()
            response = client.send("top", {
                "msg_num"    : msg_num,
                "line_count" : line_count
            })
            print(response)
        elif cmd == "":
            break
        else:
            print("Указанная команда не поддерживается !")

except Exception as e:
    print(e)
