#
# Check RSS feed for posts published in past __ hours
# If any, share post title and URL to Mastodon
#

import requests
import feedparser
##########import datetime
from datetime import datetime, timedelta
import pytz

#### GLOBAL CONSTANTS ####

# Set URL of RSS feed to check
RSS_FEED_URL = 'https://bitsrfr.com/rss/'

# Set authorization token of Mastodon account
MASTODON_ACCESS_TOKEN = ''

# Set hostname (e.g. mstdn.social) of Mastodon account
MASTODON_HOST = 'mstdn.social'

# How often (in hours) will you run this script?
HOURS_SINCE_LAST_RUN = 24

## MOVE THIS vvv INTO THE FUNCTION(S) THAT USES IT ##
current_time_utc = datetime.now(pytz.utc)

#### FUNCTIONS ####

# Parse the RSS feed
# Add each post's title, URL, and published date to rss_post_list
def parse_rss_feed():
    rss_feed = feedparser.parse(RSS_FEED_URL)
    rss_feed_entries = rss_feed.entries
    rss_post_info_dict = {}
    rss_post_list = []

    for entry in rss_feed_entries:
        rss_post_info_dict.update({'title': entry.title, 'link': entry.link, 'date': entry.published})
        rss_post_list.append(rss_post_info_dict.copy())
    return rss_post_list

'''
# NOT USED IN CURRENT IMPLEMENTATION
# Call Mastodon API, supply access token, and obtain the user account ID
# ID is needed to check status updates posted by an account
def get_mastodon_account_id():
    api_url = f'https://{MASTODON_HOST}/api/v1/accounts/verify_credentials'
    auth_header = {'Authorization': f'Bearer {MASTODON_ACCESS_TOKEN}'}

    response = requests.get(api_url, headers=auth_header)

    json_response = response.json()
    mastodon_account_id = json_response['id']
    return mastodon_account_id

# NOT USED IN CURRENT IMPLEMENTATION
# Call Mastodon API, supply account ID, and obtain account's status updates
# Extract only the content of each status update
def parse_mastodon_account_statuses(mastodon_account_id):
    api_url = f'https://{MASTODON_HOST}/api/v1/accounts/{mastodon_account_id}/statuses'

    response = requests.get(api_url)

    status_updates = response.json()

    mastodon_account_statuses = []

    for entry in status_updates:
        mastodon_account_statuses.append(entry['content'])
    return mastodon_account_statuses
'''

#### LEFT OFF HERE, WITH DATETIMEFUCKERY
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

# Look through RSS posts to see if there has been a new post in past 24 hours
# If so, see if it has been shared to Mastodon. If it has not, then post it to Mastodon
# Need to check the json response from the parse_mastodon_account_statuses function to see if I can get post dates of statuses
# Check parse_mastodon_account_statuses fields: created_at, content, application.name (would be "Postautomoton" if posted by this script)
def unsharedposts(rss_post_list):
    unsharedPosts = []

    for post in rss_post_list:
        postDate = datetimeF_ckery(post)
        lastCheck = current_time_utc - timedelta(hours=HOURS_SINCE_LAST_RUN)
        if postDate > lastCheck:
            print("Item to share to Mastodon: ")
            print(post['title'])
            unsharedPosts.append(post)
    return unsharedPosts


def POST_TO_MASTODON(unshared_posts):
    api_responses = []

    for post in unshared_posts:
        rss_post_title = post['title']
        rss_post_url = post['link']
        post_text = f'NEW POST: {rss_post_title} :: {rss_post_url}'
        api_url = f'https://{MASTODON_HOST}/api/v1/statuses'
        api_auth = {'Authorization': f'Bearer {MASTODON_ACCESS_TOKEN}'}
        api_params = {'status': f'{post_text}'}
        api_response = requests.post(api_url, data=api_params, headers=api_auth)
        api_responses.append(api_response)
    return api_responses

rss_post_list = parse_rss_feed()
# mastodon_account_id = get_mastodon_account_id()
# mastodon_account_statuses = parse_mastodon_account_statuses(mastodon_account_id)
unshared_posts = unsharedposts(rss_post_list)
api_responses = POST_TO_MASTODON(unshared_posts)

for response in api_responses:
    if response.status_code == 200:
        print("Success!")
    else:
        print(f'Failure with status code: {response.status_code}')

# Joseph Kreydt
# The Lord is our God, the Lord alone!
