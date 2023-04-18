import requests
import json
import time
import pickle
import pandas as pd
import numpy as np

df_total = pd.read_csv('./data/games_tbp.csv', index_col=0)

from igdb.wrapper import IGDBWrapper
post_url = "https://id.twitch.tv/oauth2/token?client_id=4njc2nod9cdh7wgc575ymsij8x7pli&client_secret=2g238v7i8bk5rrch8wn3g3eg45mcgq&grant_type=client_credentials"
req = requests.post(post_url)
req_dict = req.json()

wrapper = IGDBWrapper("4njc2nod9cdh7wgc575ymsij8x7pli",req_dict.get('access_token'))

# Get all the platforms
i=0
platforms = []
while True:
    try:
        byte_array = wrapper.api_request(
            'platforms',
            'fields *;offset %d; limit 500;'%(i*500)
        )
        time.sleep(0.25)
        platform_get = json.loads(byte_array)
        if platform_get:
            platforms += platform_get
            i+=1
        else:
            break
    except:
        break
    print(i)


# Get the release dates
def get_release_dates(platform_id):
    byte_array = wrapper.api_request(
        'platform_version_release_dates',
        'fields * ; where id=%d;'%platform_id
    )
    return json.loads(byte_array)[0]
get_release_dates(217)

# Get version
def get_version(version_id):
    byte_array = wrapper.api_request(
            'platform_versions',
            'fields * ; where id=%d;'%version_id
        )
    return json.loads(byte_array)[0]

for platform in platforms:
    try:
        date = get_release_dates(platform['id'])
    except:
        date = None
    platform['release_dates'] = date
    print(platform['name'])
    time.sleep(0.25)


# Get the id 282 of platform
[platform for platform in platforms if platform['id']==164]

# Save the platforms
with open('Recommendation/reddit_time/platforms.pkl', 'wb') as f:
    pickle.dump(platforms, f)

# Load the platforms
with open('Recommendation/reddit_time/platforms.pkl', 'rb') as f:
    platforms = pickle.load(f)
# To dateframe
df = pd.DataFrame(platforms)
# Transform release_dates to datetime
for platform in platforms:
    try:
        platform['release_dates'] = pd.to_datetime(platform['release_dates'], unit='s')
    except:
        pass

# Choose the platforms that are released after 2005
platforms = [platform for platform in platforms if platform['release_dates'] and platform['release_dates'].year>=2009]
# Convert the platforms to dataframe
df_platforms = pd.DataFrame(platforms)

