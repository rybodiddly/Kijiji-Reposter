# Kijiji-Reposter
Kijiji Automated Reposting Utility written in Python (version 3.7.7 at time of creation). Is completely api driven (i.e. no webscraping). Utilizes Flask, to run a local server designed to  manage the GUI interface and reposting / scheduling functions. Viable for both server and desktop environments, but if desktop, system must run 24/7 and have sleep functions disabled.


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

Login using an existing kijiji account. Or if you do not have an account, create one at kijiji.ca.


__Reposting:__

To create a reposting schedule, begin creating an ad by clicking the 'Post' icon at the top of the home screen. While entering the ad details, make sure to check the repost checkbox and enter the reposting times (eg. 07:00 am, 1:30 pm). Currently, only 8 reposting slots have been implemented. But you can edit the server.py code to allow for more.


__Force Post Ad from File:__

If you require the ability to force post an ad from file due to botched reposting, accidental deletion or other strange circumstances, you can access the force post function at `localhost:5000/force`. Note that you will first need to have an ad file saved in the users folder, both of which would have been created when initially posting an ad with a reposting schedule, and two, you will also be required to manually update the 'current_ad_id' field in the schedules.json file after the forced repost if a reposting schedule exists.


__API:__

The kijijiapi file has been intentional obfuscated to prolong patching.


__ToDo:__

- implement async
- impliment message and notification functionality
- implement message reply automation
- basic bug fixes / improvements
