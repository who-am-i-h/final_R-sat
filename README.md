
# Remote System Administartion Tool (R-SAT)

This Tool help users to maintain and manage large number of servers in a interactive way.
This tools have some prebuilt features so that user have convinient to manage the servers.

## features (CLI-version)-

- Master-mode(master): To Run commands on multiple servers at a same time it saves the user efforts for navigating to each client server for running same commands
- Dashboard(dashboard): To remove client servers, here the user can remove offline servers or servers that are not needed to monitored.
- CPU-resources(utils): just a command to see the cpu metrics at an instant.
- clients_status(clients): show the status of clients weather they are active or not.
- And at last all the communication is secured using Deffie-hellmann key-exchange + AES encryption
- File sharing (upload and download): upload : upload a file from your directory to the client server directory. download: download a file from client server to your directory.


## Features (GUI-version):-

This version is more user-friendly and help server maintainers to work on the go.

- Flask website: It contains login page for secure login
        default username: admin , password: admin
- Dashboard: for interacting with the client servers.
- delete button: this is used to remove the active/unactive client server from the administrator server.
- execute button: to enter the web-shell(an interactive command shell on web) you can run the commands on the client server using this shell.   [*] type "_dashboard" to go back to dashboard again.

- click on the IP address of the client server on the client tile to see the visual representation of cpu_metrics.
- for changing password you can click to change_password on the top.
- discord logging:- there is a custom discord bot for the web logs. you can get the logs using `!logs` on text channel.(Some work need to be done here.)
### In case you forget the password of the web GUI:-
then go and change the value of "admin" in `client.json` file to "" and then you can again login with the default credentials.

## Some important command of CLI and there uses:

- `master`: you then entered to the master dashboard and then you can select the os you want to run the commands and then you can run the command in master mode and see the output of from each server respectively.

- `dashboard`: here you can see the commands by typing `help` on the prompt and you can delete the clients here.

- `clients`: this command help you see the status of active clients along with there <server-id> and status.




### Note:-

User should avoid to execute any remote file either in web-gui or in CLI as it result to uneven behaviour of tool.













