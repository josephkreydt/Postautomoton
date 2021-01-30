#
# Check RSS feed for posts
# Check Mastodon timeline for status updates about RSS feed posts
# If no status update about post, post status update about it
#

import requests
import feedparser
import datetime
from datetime import datetime, timedelta
import pytz

# Set URL of RSS feed to check
rssfeed = 'https://bitsrfr.com/rss/'

# Set authorization token of Mastodon account
auth_token = '4-Y3nDFgrz8hV7WmbRqDAV52TiAnsQ8jeSvfbYN0g30'

# Set hostname (e.g. mstdn.social) of Mastodon account
mastodon_host = 'mstdn.social'

# How often (in days) will you run this script?
days_since_last_check = 1

# Setting date and time
dateFormat = "%a, %d %b %Y %H:%M:%S %z"
gmt = pytz.timezone('GMT')
est = pytz.timezone('EST')
now = datetime.now(est)
# make current datetime offset-aware so it can be compared with RSS post datetimes
#now = pytz.utc.localize(nowPre)
#utcOffsetOfGmt = now.strftime('%z')
#print(utcOffsetOfGmt)

def feedchecker(url):
    feed = feedparser.parse(url)

    entries = feed.entries
    post_info_dict= {}
    post_list = []

    for entry in entries:
        post_info_dict.update({'title': entry.title, 'link': entry.link, 'date': entry.published})
        post_list.append(post_info_dict.copy())
    return post_list

def getid(auth_token, mastodon_host):
    api_url = f'https://{mastodon_host}/api/v1/accounts/verify_credentials'
    auth_header = {'Authorization': f'Bearer {auth_token}'}

    response = requests.get(api_url, headers=auth_header)

    json_response = response.json()
    account_id = json_response['id']
    return account_id

def statuschecker(mastodon_host, account_id):
    api_url = f'https://{mastodon_host}/api/v1/accounts/{account_id}/statuses'

    response = requests.get(api_url)

    status_updates = response.json()

    status_update_list = []

    for entry in status_updates:
        status_update_list.append(entry['content'])
    return status_update_list

def datetimeF_ckery(rssSinglePost):
    utcNow = datetime.now()
    rssSinglePostDate = datetime.strptime(rssSinglePost['date'], "%a, %d %b %Y %H:%M:%S %Z")
    
    ### figuring out the UTC offset of the timezone of the post date
    # parse string and pull last 3 characters
    thirdToLastOfDateString = rssSinglePost['date'][-3]
    # if number, then use %z in formatting postDate
    if thirdToLastOfDateString.isdigit():
        rssSinglePostDateFinal = datetime.strptime(rssSinglePost['date'], "%a, %d %b %Y %H:%M:%S %z")
    # note: RSS feed specs only allow for either timezone code (GMT, EST, etc) or UTC offset (+0000, -0500, etc)
    # That's why we only need to check if third to last value of string is a digit
    # else they are letters, then convert to UTC offset
    else:
        # get the last 3 values of the RSS post's date string
        last3ofDateString = rssSinglePost['date'][-3:]
        # convert the last 3 values of the RSS post's date string into a datetime timezone object
        rssSinglePostTimezone = pytz.timezone(last3ofDateString)
        # Calculate the UTC offset value of the RSS post's timezone
        rssSinglePostUtcOffset = rssSinglePostDate.astimezone(rssSinglePostTimezone).strftime('%z')
        # Remove the timezone abbreviation and convert the RSS post's date to a string
        rssSinglePostDateFmt2 = rssSinglePostDate.strftime('%a, %d %b %Y %H:%M:%S')
        # Concatenate the new RSS post date string with the RSS post's UTC offset
        rssSinglePostDateFinalPre = rssSinglePostDateFmt2 + " " + rssSinglePostUtcOffset
        
        # Convert the string to datetime object
        rssSinglePostDateFinal = datetime.strptime(rssSinglePostDateFinalPre, "%a, %d %b %Y %H:%M:%S %z")
        
        return rssSinglePostDateFinal

#print(datetimeF_ckery({'title': 'Taking Ownership of Everything, Including Hidden Files, in a Directory', 'link': 'https://bitsrfr.com/taking-ownership-of-hidden-files-recursively-in-linux/', 'date': 'Wed, 27 Jan 2021 00:11:14 GMT'}))

# Look through RSS posts to see if there has been a new post in past 24 hours
# If so, see if it has been shared to Mastodon. If it has not, then post it to Mastodon
# Need to check the json response from the statuschecker function to see if I can get post dates of statuses
# Check statuschecker fields: created_at, content, application.name (would be "Postautomoton" if posted by this script)
def unsharedposts(post_list):
    unsharedPosts = []

    for post in post_list:
        postDate = datetimeF_ckery(post)
        print(postDate)
        print(now)
        lastCheck = now - timedelta(days=days_since_last_check)
        if postDate > lastCheck:
            print("Item to share to Mastodon: ")
            print(post['title'])
            unsharedPosts.append(post)
    return unsharedPosts
# Text that will be sent to Mastodon for new posts
#new_post = f'{rss_post_title}: {rss_post_url}'

post_list = feedchecker(rssfeed)
#print(post_list)
account_id = getid(auth_token, mastodon_host)
status_list = statuschecker(mastodon_host, account_id)
published_dates = unsharedposts(post_list)

'''
url = 'https://mstdn.social/api/v1/statuses'
auth = {'Authorization': 'Bearer <YOUR BEARER TOKEN/API AUTH KEY GOES HERE>'}

params = {'status': 'Mastodon API request from Pythong!'}

r = requests.post(url, data=params, headers=auth)

print(r)
'''

# Joseph Kreydt
