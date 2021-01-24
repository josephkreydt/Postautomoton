#
# Check RSS feed for posts
# Check Mastodon timeline for status updates about RSS feed posts
# If no status update about post, post status update about it
#

import requests
import feedparser

# Set URL of RSS feed to check
rssfeed = 'https://bitsrfr.com/rss/'

# Set authorization token of Mastodon account
auth_token = ''

# Set hostname (e.g. mstdn.social) of Mastodon account
mastodon_host = 'mstdn.social'

def feedchecker(url):
    feed = feedparser.parse(url)

    entries = feed.entries
    post_info_dict= {}
    post_list = []

    for entry in entries:
        post_info_dict.update({'title': entry.title, 'date': entry.published})
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

post_list = feedchecker(rssfeed)
account_id = getid(auth_token, mastodon_host)
status_list = statuschecker(mastodon_host, account_id)



'''
url = 'https://mstdn.social/api/v1/statuses'
auth = {'Authorization': 'Bearer <YOUR BEARER TOKEN/API AUTH KEY GOES HERE>'}

params = {'status': 'Mastodon API request from Pythong!'}

r = requests.post(url, data=params, headers=auth)

print(r)
'''

# Joseph Kreydt
