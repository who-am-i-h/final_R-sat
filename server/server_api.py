import threading
import socket
from flask import Flask, render_template, request, jsonify, redirect, session , url_for
from Client_mod import Client
from functools import wraps
import bcrypt
import secrets
import json
from ecc_implement import ECDH
import discord_logger
import asyncio
from DFH import Dfh_server as Dfh
from datetime import datetime

def available_algo():
    a = json.dumps({"supported":["RSADH", "ECDH"]})
    return a

def ecdh(conn, addr):
    key_gen = conn.recv(1024).decode().split("-")
    server_EC = ECDH()
    conn.send(f"{server_EC.public_key.x}-{server_EC.public_key.y}".encode())
    key = server_EC.generate_secret(int(key_gen[0]), int(key_gen[1]))
    key = str(key).encode()[:16]
    new_client = Client(key, conn, "ECCDH",True, addr)
    return new_client

def RSAdfh(conn, addr):
    key_gen = conn.recv(1024).decode().split("-")
    a, mod = int(key_gen[0]), int(key_gen[1])
    client_secret = int(key_gen[2])
    server_df = Dfh(a, mod)
    secret = server_df.private_expo()
    key = server_df.genrate_secret(client_secret)
    conn.send(str(secret).encode())
    key = str(key)[:16].encode()
    new_client = Client(key, conn, "RSADH", True, addr)
    return new_client

with open("config.json", "r") as f:
    users_db = json.load(f)
    f.close()

if users_db["admin"] == "":
    users_db = {"admin": bcrypt.hashpw(("admin").encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "TOKEN": users_db["TOKEN"]}
    with open("config.json", "w") as f:
        json.dump(users_db, f, ensure_ascii=False)
        f.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function


class ServerState:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ServerState, cls).__new__(cls)
                cls._instance.clients = []
                cls._instance.server_id = 0
        return cls._instance
    
    def add_client(self, client):
        with self._lock:
            self.clients.append(client)
    
    def get_clients(self) -> list[Client]:
        with self._lock:
            return self.clients
            
    def get_client_count(self):
        with self._lock:
            return len(self.clients)
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
server_state = ServerState()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = socket.gethostbyname(socket.gethostname())
PORT = 6969
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)
print("Server started and listening...")
def handle_clients():
    print("Client handler thread started")
    counter = 0
    while True:
        try:
            conn, addr = s.accept()
            algo = available_algo()
            conn.send(algo.encode())
            x  = conn.recv(1024)
            try:
                selected = json.loads(x)
            except:
                print(x)
            status = json.dumps({"status": True})
            conn.send(status.encode())
            if selected["selected"] == "RSADH":
                new_client = RSAdfh(conn, addr)
            elif selected["selected"] == "ECDH":
                new_client = ecdh(conn, addr)
            try:
                new_client.os = new_client.recv()                
            except:
                new_client.os = "Unidentified"
            counter += 1
            new_client.id = counter
            
            server_state.add_client(new_client)
            send_log(f"Client added. Total clients: {server_state.get_client_count()}")
            
            
        except Exception as e:
            print(f"Error in handle_clients: {e}")
            send_log(f"Error in handling clients: {e}")

def check_client(client: Client):
    try:
        client.send("..SYN..")
        client.recv()
        return True
    except socket.error:
        client.mark_offline()
        send_log(f"client \"{client.addr}\" is down!")
        return False
def send_log(log: str):
    now = datetime.now()
    formatted = now.strftime("%d-%m-%Y, %H:%M:%S")
    try:
        asyncio.run(discord_logger.push_log(formatted+" "+log))
    except:
        pass


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/verify", methods = ["POST"])
@login_required
def check_delete():
    data = request.get_json()
    with open("config.json", "r") as f:
        user_db = json.load(f)
        f.close()
    
    if bcrypt.checkpw(data["password"].encode(), user_db["admin"].encode('utf-8')):
        return jsonify({"message" : "Password correct!"}), 200
    else:
        print("wrong password")
        send_log("Wrong password for client delete!")
        return jsonify({"message" : "wrong password"}), 401


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Username and password required"}), 400

    username = data['username']
    password = data['password'].encode('utf-8')
    with open("config.json", "r") as f:
        user_db = json.load(f)
        f.close()
    if username in user_db:
        if bcrypt.checkpw(password, user_db[username].encode('utf-8')):
            session['logged_in'] = True
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"message": "Invalid password"}), 401
    else:
        return jsonify({"message": "User not found"}), 404



@app.route("/dashboard")
@login_required
def dashboard():
    clients = server_state.get_clients()
    print(f"Dashboard accessed. Current clients: {len(clients)}")
    send_log(f"Dashboard accessed. Current clients: {len(clients)}")

    for client in clients:
        check_client(client)
    return render_template("dashboard.html", servers=clients)
    
@app.route("/cpu_metrics/<int:client_id>")
@login_required
def control_panel(client_id):
    return render_template("charts.html", cid = client_id)

@app.route("/metrics", methods=['POST'])
@login_required
def get_metrics():
    clients = server_state.get_clients()
    client_id = request.get_json()
    client_id = int(client_id["server_id"])
    
    if clients:
        client_now = 0
        for client in clients:
            if client.id == client_id:
                if client.status:
                    client_now = client
                    break
        try:
            client_now.send("utils")
            from_client = client_now.recv()
            cpu, ram, disk = from_client.split("####CPUM#### ")[1].split("-")
            return jsonify({'cpu': cpu,
            "ram": ram,
            "disk": disk
            })
        except:
            return jsonify({
            'cpu': None,
            "ram": None,
            "disk": None
            })
    else:
        return ""
@app.route("/execute/<int:id>")
@login_required
def console(id):
    return render_template("index1.html", id = id)
@app.route("/execute_command", methods = ["POST"])
@login_required
def execute():
    data = request.get_json()
    command = data["command"]
    args = data["args"]  
    id = data["id"]
    clients = server_state.get_clients()
    #TODO do something with the counter // or leave it anyway
    # if int(id) > len(clients):
    #     return jsonify("No such client Exists")
    if not clients:
        return jsonify({"error": "No clients available."}), 400
    client_now = None
    for client in clients:
        if client.id == int(id):
            client_now = client
            break
    if client_now:
        from_user = command +" "+" ".join(arg for arg in args) 
        if not client_now.status:
            return jsonify("Client is offline!!, Try connecting to active clients")
        client_now.send(from_user)
        output = client_now.recv()
        return jsonify(output)
    else:
        return jsonify("Accessed client not exist....!")
@app.route("/change_password", methods=["POST"])
@login_required
def passchange():
    data = request.get_json()
    Opassword = data["Opassword"].encode('utf-8')
    Npassword = data["Npassword"]
    print(data)
    with open("config.json", "r") as f:
        user_db = json.load(f)
        f.close()
    if bcrypt.checkpw(Opassword, user_db["admin"].encode()):
        user_db["admin"] = bcrypt.hashpw(Npassword.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        with open("config.json", "w") as f:
            json.dump(user_db, f)
            f.close()
        send_log("Admin Password changed successfully")
        return jsonify({"message": "Password Change Successfully!!"})
    else:
        send_log("Wrong attempt of Login detected.")
        return jsonify({"message": "Wrong Password!!!"}), 401

@app.route("/logout")
@login_required
def out():
    session.clear()
    return redirect("/")
@app.route("/change")
@login_required
def pchange():
    return render_template("change_password.html")

@app.route("/delete/<int:client_id>")
@login_required
def delete_client(client_id):
    clients = server_state.get_clients()
    with server_state._lock:
        for client in clients:
            if client.id == client_id:
                if client.status:
                    client.send("####TERMINATE####")
                    clients.remove(client)
                    send_log(f" Active client {client.addr} removed successfully!")
                    return redirect("/dashboard")
                else:
                    clients.remove(client)
                    
                    send_log(f" Active client {client.addr} removed successfully!")
            
                    

                    return redirect("/dashboard")
                    

if __name__ == '__main__':
    try:
        discord_bot_thread = threading.Thread(target=discord_logger.start_bot, args=(users_db["TOKEN"],), daemon=True)
        discord_bot_thread.start()
    except:
        print("some error happened while connecting to the bot!!")
    client_handler = threading.Thread(target=handle_clients, daemon=True)
    client_handler.start()
    print("Starting Flask app...")
    app.run(debug=False, port=5000, threaded=True, host="0.0.0.0")
