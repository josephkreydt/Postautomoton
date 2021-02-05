# Postautomoton
A Python 3 script to automate Mastodon status updates via API
----

- Posts status updates about new RSS feed posts to Mastodon
- Designed to be scheduled with [Cron](https://crontab.guru/examples.html)
- Does not need 'sudo' to run
- Edit the CONSTANTS in the beginning portion of the script to suit your needs
- You will need [Python 3](https://www.python.org/downloads/) installed
- Install [pip](https://pip.pypa.io/en/stable/installing/) for ease of installing dependencies

Dependencies:
- [datetime](https://docs.python.org/3/library/datetime.html)(part of Python standard library)
- [Requests](https://2.python-requests.org/en/master/user/install/#install)
- [feedparser](https://pypi.org/project/feedparser/)
- [pytz](https://pypi.org/project/pytz/)

To make executable on *nix systems for file owner: 
- sudo chmod u+x postautomoton.py

To make executable on *nix systems for all users:
- sudo chmod +x postautomoton.py

----
Joseph Kreydt
The Lord is our God, the Lord alone!
