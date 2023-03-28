import socket
import json
import requests

config = open("config.json", "r")
config = config.read()
config = json.loads(config)
if not "server" in config:
  print("[ERROR] CONFIG DOES NOT CONTAINS COMPLETE SERVER INFO. PLEASE ADD SEVER IN CONFIG FILE")
  exit()
else:
  server = config['server']
if not server['address']:
  print("[ERROR] CONFIG DOES NOT CONTAINS COMPLETE SERVER INFO. PLEASE ADD SEVER IN CONFIG FILE")
  exit()
if not server['port']:
  print("[ERROR] CONFIG DOES NOT CONTAINS COMPLETE SERVER INFO. PLEASE ADD SEVER IN CONFIG FILE")
  exit()
if server['address'] == "public":
  try:
    response = requests.get("http://ifconfig.me")
    ip_address = response.content.decode('utf-8')
  except requests.exceptions.ConnectionError:
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print("[ERROR] NO INTERNET CONNECTION")
elif server['address'] == "local":
  hostname = socket.gethostname()
  ip_address = socket.gethostbyname(hostname)
else:
  ip_address = server['address']
HOST, PORT = ip_address, server['port']
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
try:
  listen_socket.bind((HOST, PORT))
except TypeError:
  print("[ERROR] INVALID PORT OR IP. PLEASE CHANGE CONIFG")
  exit()
except OSError:
  hostname = socket.gethostname()
  ip_address = socket.gethostbyname(hostname)
  HOST, PORT = ip_address, server['port']
  listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
except OSError:
  print("[ERROR] PORT OR IP ALREADY IN USE. PLEASE CHANGE CONFIG")
  exit()
listen_socket.listen(1)
def link(uri, label=None):
  if label is None:
    label = uri
  parameters = ''
  escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'
  return escape_mask.format(parameters, uri, label)
linked = link(f"http://{ip_address}:{PORT}")
print(f"Serving HTTP on \033[93m{linked}\033[00m\n")
print("\033[96mLogs:\033[00m")
if "redirects" in config:
  redirects = config['redirects']
  rdr_state = True
else:
  rdr = False
if "paths" in config:
  paths = config['paths']
  path_state = True
else:
  path_state = False
while True:
  client_connection, client_ip = listen_socket.accept()
  client_ip = client_ip[0]
  request_data = client_connection.recv(1024)
  split_data = request_data.decode().split()
  req_path = split_data[1:2][0]
  if path_state == True and req_path in paths:
    filename = "src/" + paths[req_path]
    html = open(filename, "r")
    html = html.read()
    http_response = f"""\
HTTP/1.1 200 OK

{html}
"""
    print("[INFO] \033[92mGET " + req_path + " 200 OK\033[00m   IP: " +
          client_ip)
  elif rdr_state == True and req_path in redirects:
    route = config['redirects'][req_path]
    http_response = f"""\
HTTP/1.1 301 Moved Permanently
Location: {route}

"""
    print("[INFO] \033[92mGET " + req_path + " 301 Redirected\033[00m   IP: " +
          client_ip)
  else:
    http_response = """\
HTTP/1.1 404 Not Found

404 Not Found
"""
    print("[INFO] \033[31mGET " + req_path + " 404 Not Found\033[00m  IP: " +
          client_ip)
  client_connection.sendall(http_response.encode("utf-8"))
  client_connection.close()
