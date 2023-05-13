import pickle
import pandas as pd
import numpy as np
import json
import requests
import time
import os

# Get the access token
from igdb.wrapper import IGDBWrapper
post_url = "https://id.twitch.tv/oauth2/token?client_id=4njc2nod9cdh7wgc575ymsij8x7pli&client_secret=2g238v7i8bk5rrch8wn3g3eg45mcgq&grant_type=client_credentials"
req = requests.post(post_url)
req_dict = req.json()

# Get the wrapper
wrapper = IGDBWrapper("4njc2nod9cdh7wgc575ymsij8x7pli", req_dict.get('access_token'))


def get_version(version_id):
    byte_array = wrapper.api_request(
            'platform_versions',
            'fields * ; where id=%d;' % version_id
        )
    time.sleep(0.25)
    return json.loads(byte_array)[0]

def get_release_dates(platform_version_release_date_id):
    byte_array = wrapper.api_request(
        'platform_version_release_dates',
        'fields * ; where id=%d;' % platform_version_release_date_id
    )
    time.sleep(0.25)
    return json.loads(byte_array)[0]

if not os.path.exists('./data/games.pkl'):
    i=0
    games_list = []
    while True:
        byte_array = wrapper.api_request(
                'games',
                'fields age_ratings,aggregated_rating,aggregated_rating_count,alternative_names,artworks,bundles,category,checksum,collection,cover,created_at,dlcs,expanded_games,expansions,external_games,first_release_date,follows,forks,franchise,franchises,game_engines,game_localizations,game_modes,genres,hypes,involved_companies,keywords,language_supports,multiplayer_modes,name,parent_game,platforms,player_perspectives,ports,rating,rating_count,release_dates,remakes,remasters,screenshots,similar_games,slug,standalone_expansions,status,storyline,summary,tags,themes,total_rating,total_rating_count,updated_at,url,version_parent,version_title,videos,websites; offset %d; limit 500;'%(i*500)
                )
        i+=1
        games = json.loads(byte_array)
        games_list.extend(games)
        print(i)
        time.sleep(0.2)
        if games==[]:
            break
    with open('./data/games.pkl','wb') as f:
        pickle.dump(games_list, f, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open('./data/games.pkl','rb') as f:
        games_list = pickle.load(f)

# Get all the platforms
if not os.path.exists('./data/platforms.pkl'):
    platforms = []
    byte_array = wrapper.api_request(
                'platforms',
                'fields *; limit 500;'
            )
    time.sleep(0.25)
    print(byte_array)
    platform_get = json.loads(byte_array)

    # Save the platforms
    with open('./data/platforms.pkl', 'wb') as handle:
        pickle.dump(platform_get, handle)
else:
    with open('./data/platforms.pkl', 'rb') as handle:
        platforms = pickle.load(handle)


# Get the versions of the platforms
'''
For example, the versions of the platform PS4 are PS4 Pro, PS4 Slim, PS4.
'''
if not os.path.exists('./data/version.pkl'):
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
    with open('./data/version.pkl', 'wb') as handle:
        pickle.dump(version_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open('./data/version.pkl', 'rb') as handle:
        version_dict = pickle.load(handle)


# Get the release dates of the platforms.
if not os.path.exists('./data/console_released_date.pkl'):
    # Choose the platform with category 1 or 5
    console_dict = {}
    for platform in platforms:
        try:
            # These are the platforms we want, i.e., console games platforms.
            if platform['category'] in [1, 5]:
                console_dict[platform['name']] = version_dict[platform['name']]
        except:
            pass
    console_released_date_dict = {}
    for console_name, console_versions in console_dict.items():
        print(console_name)
        for version in console_versions:
            try:
                date = get_release_dates(version['platform_version_release_dates'][-1])
                console_released_date_dict[console_name+'-'+version['name']] = date
                print(console_name+version['name'])
            except:
                pass
    with open('./data/console_released_date.pkl', 'wb') as handle:
        pickle.dump(console_released_date_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    pass 

# Save the console released date to csv file.
if not os.path.exists('./data/console_released_date.csv'):
    # Load the console released date dict.
    with open('./data/console_released_date.pkl', 'rb') as handle:
        console_released_date_dict = pickle.load(handle)
    
    # Change to dataframe.
    df_console_released_date = pd.DataFrame.from_dict(console_released_date_dict, orient='index')
    # Change the date to datetime
    df_console_released_date['date'] = pd.to_datetime(df_console_released_date['date'], unit='s')
    # Choose the console game platforms realeased after 2009.
    df_console_released_date = df_console_released_date[df_console_released_date['date'] > '2009-01-01']
    # Save the dataframe
    df_console_released_date.to_csv('./data/console_released_date.csv')

# Get the definition of the genres.
# 1. Action 2. Adventure 3. Fighting 4. Misc 5. Platform 6. Puzzle 7. Racing 8. Role-Playing 9. Shooter 10. Simulation 11. Sports 12. Strategy
if not os.path.exists("./data/genres_igdb.pkl"):
    genres_name = []
    byte_array = wrapper.api_request(
            'genres',
                    'fields *; limit 500;' 
                )
    time.sleep(0.25)
    genres_get = json.loads(byte_array)
    if genres_get:
        genres_name += genres_get

    df_genres_name = pd.DataFrame(genres_name)
    df_genres_name.to_pickle('./data/genres_igdb.pkl')