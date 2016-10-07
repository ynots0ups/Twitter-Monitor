#!/usr/bin/env python2.7

import json
import smtplib
import datetime
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

#################################################
#                                               #
#               Tweet-Monitor.py                #
#                     v3.0                      #
#               A twitter monitor               #
#                                               #
#             By s0ups (@ynots0ups)             #
#                                               #
#  https://github.com/ynots0ups/Tweet-Monitor   #
#                                               #
#################################################
# https://pypi.python.org/pypi/twitter


########### Shit For You To Change ##############
#
# Twitter API credz
#
ACCESS_TOKEN    = ''
ACCESS_SECRET   = ''
CONSUMER_KEY    = ''
CONSUMER_SECRET = ''

#
# Accounts to monitor
#
ACCOUNT_LIST = 'ynots0ups, dc225'

#
# Full monitor accounts
# Must use Twitter ID!
#
# @ynots0ups => 1151671417, @dc225 => 1120271370
#
FULL_MONITOR = ['1151671417', '1120271370']

#
# Keywords
#
KEYWORD_LIST = ['drink', 'all', 'the', ' booze ', 'hack', 'all', 'the', 'things']

#
# Mail Settings
#
SERVER = 'localhost'
SENDER = ''
RECIPIENT = ''
E_SIGNATURE = '\n\n\n- s0ups wuz here'

#################################################
################## The Code #####################

# Search the tweet body for keywords
def ParseTweet(tweet):
    for keyword in KEYWORD_LIST:
        if keyword.lower() in tweet.lower():
            return keyword 
    return 0

# What to do if we have a hit? Get notified, son!
def ProcessHit(tweet, keyword):
    timestamp   = datetime.datetime.fromtimestamp(int(tweet['timestamp_ms'])/1000).strftime('%Y-%m-%d %H:%M:%S')
    screenname  = tweet['user']['screen_name']
    e_subject   = 'Found tweet from @{} matching keyword: {}'.format(screenname, keyword)
    e_body      = 'Time of Tweet: {}\nUsername: @{}\nTweet Content: "{}"\nKeyword Hit: {}\nLink: https://twitter.com/{}/status/{}{}'.format(timestamp, screenname, tweet['text'].encode('utf-8'), screenname, keyword, tweet['id'], E_SIGNATURE)
    SendNotify(e_subject, e_body)

def SendNotify(subject, body):
    message = "From %s\nTo: %s\nSubject: %s\n\n%s"%(SENDER, RECIPIENT, subject, body)
    try:
        smtpObj = smtplib.SMTP(SERVER)
        smtpObj.sendmail(SENDER, RECIPIENT, message)
    except:
        file = open("Tweet-Monitor.log","a")
        file.write(subject + "\r\n" + body + "\r\n\r\n")
        file.close()
    return

# Connect to the Twitter API
oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter_stream = TwitterStream(auth=oauth)

fullmonitored = ",".join(FULL_MONITOR)

# Start receiving data from twitter matching the accounts we are monitoring
iterator = twitter_stream.statuses.filter(track=ACCOUNT_LIST,follow=fullmonitored)

# Once we get a hit we will do shit
for tweet in iterator:
    # Check if it was a delete event - ignore if so
    if 'delete' in tweet:
        continue
    else:
        # Check if it's a fully monitored account
        for id in FULL_MONITOR:
            if tweet['user']['id_str'] == id:
                ProcessHit(tweet, "*Full Monitored*")
            # Otherwise check for keywords
            else:
                result = ParseTweet(tweet['text'])
                if result:
                    ProcessHit(tweet, result)
                    print tweet