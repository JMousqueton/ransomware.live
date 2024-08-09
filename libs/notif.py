import http.client, urllib
from dotenv import load_dotenv
import os, json
import requests
from datetime import datetime, timezone
from mastodon import Mastodon
import tweepy

def tobluesky(post_title,group):
    try:
        from ransomwarelive import stdlog, errlog
        stdlog('Send Bluesky notification')
        url = os.environ.get('BLUESKY_URL')
        handle = os.environ.get('BLUESKY_HANDLE')
        password = os.environ.get('BLUESKY_APP_PASSWORD')
        resp = requests.post(url,
                    json={"identifier": handle, "password": password},
                )
        resp.raise_for_status()
        session = resp.json()
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        text= "According to https://ransomware.live, " + group + " ransomware group has added " + post_title + " to its victims. "
        startoffset = 13
        uri = "https://ransomware.live"
        endoffset = 36
            # Required fields that each post must include
        post = {
                "$type": "app.bsky.feed.post",
                "text": text,
                "createdAt": now,
                "facets": [{
                    "index": {
                    "byteStart": startoffset,
                    "byteEnd": endoffset,
                    },
                "features": [{
                    "$type": "app.bsky.richtext.facet#link",
                    "uri": uri,
                    }],
                }],
            }
        resp = requests.post("https://bsky.social/xrpc/com.atproto.repo.createRecord",
                    headers={"Authorization": "Bearer " + session["accessJwt"]},
                    json={
                        "repo": session["did"],
                        "collection": "app.bsky.feed.post",
                        "record": post,
                    },
            )
    except Exception as e:
        errlog(f'Error posting on bluesky : {e}')

def tomattermost(post_title,group):
    from ransomwarelive import stdlog, errlog
    stdlog('Send Mattermost notification')
    webhook=os.environ.get('MATTERMOST_WEBHOOK')
    # Prepare the payload
    message = "⚠️ **" + group + "** ransomware group has added **" + post_title + "** to its victims. "
    payload = {'text': message,
            'username': 'Ransomware.live',
            'icon_url': "https://ransomware.live/ransomwarelive.png"
            }
    # Headers for the HTTP request
    headers = {'Content-Type': 'application/json'}
    # Perform the POST request to the Mattermost webhook
    response = requests.post(webhook, data=json.dumps(payload), headers=headers)
    # Check for successful transmission
    if not response.status_code == 200:
        stdlog("Error Mattermost : " + response.status_code)


def totwitter(post_title, group):
    try:
        from ransomwarelive import stdlog, errlog
        stdlog('Send Twitter notification')
        client = tweepy.Client(
            consumer_key=os.environ.get('TWITTER_CONSUMER_KEY'),
            consumer_secret=os.environ.get('TWITTER_CONSUMER_SECRET'),
            access_token=os.environ.get('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
            )
        status = str(group) + ' : ' + str(post_title) + ' https://www.ransomware.live/#/group/' + str(group)
        client.create_tweet(text=status)
    except TypeError as te:
        honk('sharedutils: ' + 'twitter tweepy unsatisfied: ' + str(te))

def todiscord(post_title, group):
    from ransomwarelive import stdlog, errlog
    stdlog('Send Discord notification')
    webhook=os.environ.get('DISCORD_WEBHOOK')
    # avoid json decode errors by escaping the title if contains \ or "
    post_title = post_title.replace('\\', '\\\\').replace('"', '\\"')
    discord_data = '''
    {
    "content": "`%s`",
    "embeds": [
        {
        "color": null,
        "author": {
            "name": "%s",
            "url": "https://www.ransomware.live/#/profiles?id=%s",
            "icon_url": "https://avatars.githubusercontent.com/u/10137"
        }
        }
    ]
    }''' % (post_title, group, group)
    discord_json = json.loads(discord_data)
    dscheaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    try:
        hookpost = requests.post(webhook, json=discord_json, headers=dscheaders)
    except requests.exceptions.RequestException as e:
        errlog('Error sending to discord webhook: ' + str(e))
    if hookpost.status_code == 204:
        return True
    if hookpost.status_code == 429:
        errlog('Error: Discord webhook rate limit exceeded')
    else:
        errlog('Received discord webhook error resonse ' + str(hookpost.status_code) + ' with text ' + str(hookpost.text))
    return False


def toMastodon(post_title, group_name):
    from ransomwarelive import stdlog, errlog
    stdlog('Send Mastodon notification')
    mastodon = Mastodon(
    access_token =  os.getenv('MASTODON_TOKEN'),
    api_base_url = 'https://infosec.exchange/'
    )
    mastodon.status_post("🏴‍☠️ A new victim called "+ post_title + " has been claimed by #Ransomware group "+ group_name+'. More information at https://ransomware.live')

def toPushover(post_title, group_name):
    from ransomwarelive import stdlog, errlog
    stdlog('Send Pushover notification')
    USER_KEY=os.getenv('PUSH_USER')
    API_KEY= os.getenv('PUSH_API')
    MESSAGE = "<b>" + post_title +  "</b> est victime du ransomware <b>" + group_name + "</b>"
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
              "token": API_KEY,
              "user": USER_KEY,
              "message": MESSAGE,
              "html": 1
            }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()


def toteams(post_title, group):
    from ransomwarelive import stdlog, errlog
    stdlog('Send Teams notification')
    # avoid json decode errors by escaping the title if contains \ or "
    post_title = post_title.replace('\\', '\\\\').replace('"', '\\"')
    teams_data = '''
    {
    "type":"message",
    "attachments":[
        {
            "contentType":"application/vnd.microsoft.card.adaptive",
            "contentUrl":null,
            "content":{
                "type": "AdaptiveCard",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "%s",
                        "isSubtle": true,
                        "wrap": true
                    }
                ],
                "actions": [
                    {
                        "type": "Action.OpenUrl",
                        "title": "%s",
                        "url": "https://www.ransomware.live/#/profiles?id=%s"
                    }
                ],
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.4"
            }
        }
    ]
    }''' % (post_title, group, group)
    try:
        load_dotenv()
        hook_uri = os.environ.get('MS_TEAMS_WEBHOOK')
        hookpost = requests.post(hook_uri, data=teams_data, headers={'Content-Type': 'application/json'})
    except requests.exceptions.RequestException as e:
        errlog('Error sending to microsoft teams webhook: ' + str(e))
    if hookpost.status_code == 200:
        return True
    if hookpost.status_code == 429:
        errlog('Microsoft teams webhook rate limit exceeded')
    else:
        errlog('Recieved microsoft teams webhook error resonse ' + str(hookpost.status_code) + ' with text ' + str(hookpost.text))
    return False
