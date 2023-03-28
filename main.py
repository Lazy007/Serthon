import socket, json, requests, os, sys
black, red, green, orange, blue, purple, cyan, lightgrey, darkgrey, lightred, lightgreen, yellow, lightblue, pink, lightcyan, norm = '\033[30m', '\033[31m', '\033[32m', '\033[33m', '\033[34m', '\033[35m', '\033[36m', '\033[37m', '\033[90m', '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[0m'
args = sys.argv[1:]
if not args:
  filename = "config.json"
elif args[0] in ["-f", "--filename"]:
  if not args[1]:
    print("USAGE: python3 main.py -f filename")
  else:
    filename = args[1]
elif args[0] in ["--help", "-h"]:
  print("USAGE: python3 main.py [COMMAND] ")
  print("                       -h, --help       shows this.")
  print("                       -f, --filename   use to set config file name. DEFAULT: config.json")
  exit()
else:
  print("USAGE: python3 main.py -f 'filename'")
if not os.path.isfile(filename):
  print(f"[{red}ERROR{norm}] NO CONFIG FILE FOUND WITH NAME {filename}. CREATE ONE AS 'config.json' OR TO USE DIFFERENT FILENAME RUN SERTHON AS 'python3 main.py -f filename' ")
  exit()
config = open(filename, "r")
config = config.read()
try:
  config = json.loads(config)
except ValueError:
  print(f"[{red}ERROR{norm}] SYNTAX ERROR IN {filename}")
  exit()
if not "server" in config:
  print(f"[{red}ERROR{norm}] CONFIG DOES NOT CONTAINS SERVER INFO. PLEASE ADD SEVER IN CONFIG FILE")
  exit()
else:
  server = config['server']
if not "address" in server or not "port" in server:
  print(f"[{red}ERROR{norm}] CONFIG DOES NOT CONTAINS ADDRESS OR PORT INFO. PLEASE ADD SEVER IN CONFIG FILE")
  exit()
if server['address'] == "public":
  try:
    response = requests.get("http://ifconfig.me")
    ip_address = response.content.decode('utf-8')
  except requests.exceptions.ConnectionError:
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"[{red}ERROR{norm}] NO INTERNET CONNECTION")
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
  print(f"[{red}ERROR{norm}] INVALID PORT OR IP. PLEASE CHANGE CONIFG")
  exit()
except OSError:
  if server['address'] == "local":
    print(f"[{red}ERROR{norm}] INVALID PORT OR IP. PLEASE CHANGE CONIFG")
    exit()
  hostname = socket.gethostname()
  ip_address = socket.gethostbyname(hostname)
  HOST, PORT = ip_address, server['port']
  listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
except OSError:
  print(f"[{red}ERROR{norm}] PORT OR IP ALREADY IN USE. PLEASE CHANGE CONFIG")
  exit()
listen_socket.listen(1)
def link(uri, label=None):
  if label is None:
    label = uri
  parameters = ''
  escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'
  return escape_mask.format(parameters, uri, label)
linked = link(f"http://{ip_address}:{PORT}")
print(f"Serving HTTP on {yellow}{linked}{norm}\n")
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
    print(f"[{blue}INFO{norm}] {lightgreen}GET {req_path} 200 OK{norm}   IP: {client_ip}")
  elif rdr_state == True and req_path in redirects:
    route = config['redirects'][req_path]
    http_response = f"""\
HTTP/1.1 301 Moved Permanently
Location: {route}

"""
    print(f"[{blue}INFO{norm}] {lightgreen}GET {req_path} 301 Redirected{norm}   IP: {client_ip}")
  else:
    http_response = """\
HTTP/1.1 404 Not Found

404 Not Found
"""
    print(f"[{blue}INFO{norm}] {red}GET {req_path} 404 Not Found{norm}  IP: {client_ip}")
  client_connection.sendall(http_response.encode("utf-8"))
  client_connection.close()