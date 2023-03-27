import socket
import json
HOST, PORT = '0.0.0.0', 8888
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
listening_ip = listen_socket.getsockname()[0]
def link(uri, label=None):
    if label is None: 
        label = uri
    parameters = ''
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'
    return escape_mask.format(parameters, uri, label)
linked = link(f"http://{listening_ip}:{PORT}")
print(f"Serving HTTP on \033[93m{linked}\033[00m\n")
print("\033[96mLogs:\033[00m")
paths = open("server.conf", "r")
paths = paths.read()
paths = json.loads(paths)
while True:
    client_connection, client_address = listen_socket.accept()
    request_data = client_connection.recv(1024)
    split_data = request_data.decode().split()
    req_path = split_data[1:2][0]
    if 'Referer:' in split_data:
        ip = split_data[34]
    else:
        ip = split_data[32]
    if req_path in paths:
        filename = "src/" + paths[req_path]
        html = open(filename, "r")
        html = html.read()
        http_response = f"""\
HTTP/1.1 200 OK

{html}
"""
        print("[INFO] \033[92mGET " + req_path +" 200 OK\033[00m   IP: " + ip)
    else:
        http_response = """\
HTTP/1.1 404 Not Found

Invalid Path
"""
        print("[INFO] \033[31mGET " + req_path +" 404 Not Found\033[00m  IP: " + ip)
    client_connection.sendall(http_response.encode("utf-8"))
    client_connection.close()
