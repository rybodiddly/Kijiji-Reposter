# Kijiji-Reposter
Kijiji Automated Reposting Utility written in Python. Is completely api driven (i.e. no webscraping). Utilizes Flask, to run a local server designed to  manage the GUI interface and reposting / scheduling functions.

__Requirements:__
```
wheel
Flask-WTF
Flask
xmltodict
httpx
apscheduler
urllib3
```

__Usage:__

Edit the secret key argument on line 21 in server.py. Then run:
```
python server.py
```

__Connections:__

Once server is running, connect to either of the addresses listed below in a web browser. Or if running on a network, connect to the ip and port 5000 of computer running the kijiji reposter server.
```
localhost:5000/
127.0.0.1:5000/
```

__Accounts:__

Login using your kijiji account. Or if you do not have an account, create one at kijiji.ca.
