import pickle
import pandas as pd
import numpy as np
import json
import requests
import time
import os

from igdb.wrapper import IGDBWrapper
post_url = "https://id.twitch.tv/oauth2/token?client_id=4njc2nod9cdh7wgc575ymsij8x7pli&client_secret=2g238v7i8bk5rrch8wn3g3eg45mcgq&grant_type=client_credentials"
req = requests.post(post_url)
req_dict = req.json()

wrapper = IGDBWrapper("4njc2nod9cdh7wgc575ymsij8x7pli",req_dict.get('access_token'))

# Get all the platforms
if not os.path.exists('./data/platforms.pickle'):
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
            else:
                break
        except:
            break


    # Save the platforms
    with open('./data/platforms.pickle', 'wb') as handle:
        pickle.dump(platforms, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open('./data/platforms.pickle', 'rb') as handle:
        platforms = pickle.load(handle)

def get_version(version_id):
    byte_array = wrapper.api_request(
            'platform_versions',
            'fields * ; where id=%d;'%version_id
        )
    time.sleep(0.25)
    return json.loads(byte_array)[0]

def get_release_dates(platform_version_release_date_id):
    byte_array = wrapper.api_request(
        'platform_version_release_dates',
        'fields * ; where id=%d;'%platform_version_release_date_id
    )
    time.sleep(0.25)
    return json.loads(byte_array)[0]

if not os.path.exists('./data/version.pickle'):
    version_dict = {}
    for platform in platforms:
        # Get the version
        try:
            version_list = []
            for version_id in platform['versions']:
                version = get_version(version_id)
                version_list.append(version)
            version_dict[platform['name']] = version_list
            print(platform['name'])
        except:
            pass

    # Save the version
    with open('./data/version.pickle', 'wb') as handle:
        pickle.dump(version_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open('./data/version.pickle', 'rb') as handle:
        version_dict = pickle.load(handle)

# Choose the platform with category 1 or 5
console_dict = {}
for platform in platforms:
    try:
        if platform['category'] in [1,5]:
            console_dict[platform['name']] = version_dict[platform['name']]
    except:
        pass

if not os.path.exists('./data/console_date.pickle'):
    console_date_dict = {}
    for console_name, console_versions in console_dict.items():
        print(console_name)
        for version in console_versions:
            try:
                date = get_release_dates(version['platform_version_release_dates'][-1])
                console_date_dict[console_name+'-'+version['name']] = date
                print(console_name+version['name'])
            except:
                pass
    with open('./data/console_date.pickle', 'wb') as handle:
        pickle.dump(console_date_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open('./data/console_date.pickle', 'rb') as handle:
        console_date_dict = pickle.load(handle)

# Change to dataframe
df_console_date = pd.DataFrame.from_dict(console_date_dict, orient='index')
# Change the date to datetime
df_console_date['date'] = pd.to_datetime(df_console_date['date'], unit='s')
# Choose the date after 2009
df_console_date = df_console_date[df_console_date['date'] > '2009-01-01']

# Save the dataframe
df_console_date.to_csv('./data/console_date.csv')

df_platform = pd.DataFrame.from_dict(platforms)
