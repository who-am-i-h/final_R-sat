import asyncio
from Client_mod import Client
import termcolor

def color(text, col):
    return termcolor.colored(text, col)

class Master():
    def __init__(self, clients: list[Client]):
        self.clients = clients

    async def execute(self, command, avl_client:Client):
        avl_client.send(command)
        return avl_client.addr, avl_client.recv()
    
    async def master(self, command):
        avl_clients = []
        for client in self.clients:
            if client.status:
                avl_clients.append(client)
        results = {}
        async with asyncio.TaskGroup() as tg:
            for avl_client in avl_clients:
                tg.create_task(self._execute_task(command, avl_client, results))
        return results
    async def _execute_task(self, command, avl_client, results):
        addr, result = await self.execute(command, avl_client)
        results[addr] = result

def master_dashboard(clients: list[Client]):
    print(color("+"*49, "green"))
    print(color("Welcome to Master Dashboard!!", "yellow"), color("here you can commands for multiple servers at same time", "blue"))
    avl_os = {}
    for client in clients:
        # if client in list(avl_os.keys()):
        #     avl_os[client] += 1
        # else:
        #     avl_os[client] = 1
        #TODO implement this everytime in place of above
        avl_os[client.os] = avl_os.get(client.os, 0) + 1

    print("We have these os_available:----")
    for i, os in enumerate(list(avl_os.keys())):
        print(f"[{color(f"{i+1}", "blue")}]", color(f"{os}-->", "green"), avl_os[os])
    while True:
        try:
            user = int(input(f'''Choose the OS to run the command in master mode: '''))
            if user < 0 and user > len(list(avl_os.keys())):
                raise ValueError
            break
        except ValueError:
            print("Wrong input try again:...")
        except Exception as e:
            print("some unknown error happend ", e)
            break
    selected_os = list(avl_os.keys())[user-1]
    to_be_executed = [client for client in clients if client.os == selected_os]

    executor = Master(to_be_executed) 
    prompt = input(f"{color("MASTER:-> ", "red")}[{color("*", "blue")}]~! ")
    results = asyncio.run(executor.master(prompt))
    print(color("Execution Results:", "cyan"))
    for addr, result in results.items():
        print(f"Client {color(addr, 'yellow')}: {color(result, 'green')}")

    
        

    
    
