import json
import pickle
import requests
import re
import os
from time import sleep
import pandas as pd
import time
import matplotlib.pyplot as plt

if not os.path.exists('./data/history.pickle'):
    history_url = "https://raw.githubusercontent.com/RegExrTech/SwapBot/master/database/gamesale-swaps.json"
    history = requests.get(history_url).json()['reddit']
    # Save the dictionary
    with open('./data/history.pickle', 'wb') as handle:
        pickle.dump(history, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open('./data/history.pickle', 'rb') as handle:
        history = pickle.load(handle)

# Split by first - and return a tuple
def split_by_dash(string):
    return tuple(string.split(' - ', 1))

if not os.path.exists('./data/transformed_data.pickle'):
    # Processed data
    pattern = r"/r/(\w+)/"
    transformed_data = {}
    wrong_data = {}
    for key, value_list in history.items():
        for value in value_list:
            try:
                user, link = split_by_dash(value)
                # Use re to get the string between "r/" and "/" in the link
                _type = re.search(pattern, link).group(1)
                transformed_data.setdefault(key, []).append({
                    'user': user,
                    'link': link,
                    'type': _type
                })
            except ValueError:
                wrong_data.setdefault(key, []).append(value)


# # Get all the key 'gameswap'
# swap_dict = {}
# for key, value_list in transformed_data.items():
#     for value in value_list:
#         if value['type'] == 'gameswap':
#             swap_dict.setdefault(key, []).append(value)
# # Get the total number of items in swap_dict
# sum([len(value) for value in swap_dict.values()])
# # Get the item in swap_dict
# list(swap_dict.items())[0]
#
# swap_dict.get('MrAce2C'.lower())
# swap_dict.get('rdmentalist'.lower())

# Get the total number of items in transformed_data
# sum([len(value) for value in transformed_data.values()])


# import praw
#
# reddit = praw.Reddit(
#     client_id="kwWra4Twk0boTlmkSKn0Bg",
#     client_secret="8Z1IHc3epigPKp44Txyhsq1Bl3OI4w",
#     user_agent="get transaction history",
# )
# reddit.read_only = True
#
# url_comment = 'https://www.reddit.com/r/gamesale/comments/4c34l2/-/d72rnbm'
# submission = reddit.submission(url=url_comment)
# submission.comments.replace_more(limit=0)
# comments = submission.comments.list()


# Get the comment
def get_comment(url):
    json_raw = requests.get(url+'.json', headers = {'User-agent': 'your bot 314151926'})
    # Read the list in a
    try:
        _comment = json_raw.json()[1]['data']['children'][0]['data']
        sleep(0.15)
        return _comment
    except IndexError:
        return None

if not os.path.exists('./data/transformed_data.pickle'):
    start_time = time.time()
    i=0
    start = 0
    for key, value_list in list(transformed_data.items())[start:] :
        for value in value_list:
            if value.get('comment') is None:
                value['comment'] = get_comment(value['link'])
        i+=1
        print(i, time.time() - start_time)

    # Save the dictionary
    with open('./data/transformed_data.pickle', 'wb') as handle:
        pickle.dump(transformed_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open('./data/transformed_data.pickle', 'rb') as handle:
        transformed_data = pickle.load(handle)

# For each comment, we want the following information:
# - author
# - body
# - created_utc
# - permalink
# - replies['data']['children'][0]['data']
keys = ['author', 'body', 'created_utc', 'permalink']
reply_keys = ['author', 'body']

simplified_data = {}
for key, value_list in transformed_data.items():
    for value in value_list:
        if value.get('comment') is not None:
            simplified_data.setdefault(key, []).append({k: value['comment'][k] for k in keys})
            try:
                reply = value['comment']['replies']['data']['children'][0]['data']
                for reply_key in reply_keys:
                    if reply.get(reply_key) is not None:
                        simplified_data[key][-1].setdefault('reply_%s'%reply_key,  reply[reply_key])
            except Exception:
                pass


flatten_dict = {}
for key, value_list in simplified_data.items():
    for index, value in enumerate(value_list):
        flatten_dict.setdefault(key+"_%d" % index,value)

df = pd.DataFrame(flatten_dict).T
# index to a column
df.reset_index(inplace=True)

pattern = r"/r/(\w+)/"
df['type'] = df['permalink'].apply(lambda x: re.search(pattern, x).group(1).lower())
# Transform to human-readable time
df['created_utc'] = pd.to_datetime(df['created_utc'], unit='s')
# Get the unique type
df['type'].unique()



# Get the cumulative sum of the number of transactions per day of type 'gameswap'
plt.clf()
df[df['type'] == 'gameswap'].groupby('created_utc').count()['index'].cumsum().plot()
df[df['type'] == 'gamesale'].groupby('created_utc').count()['index'].cumsum().plot()
df[df['type'] == 'mushroomkingdom'].groupby('created_utc').count()['index'].cumsum().plot()
plt.legend(['gameswap', 'gamesale', 'mushroomkingdom'])
plt.show()

# Training data with type not equal to 'mushroomkingdom' with columns ['body', 'type']
df_train = df[(df['type'] != 'mushroomkingdom') & (df['author']!= 'SwapNSalebot')][['body', 'type']]
# Remove the rows with body is '[deleted]' or '[removed]'
df_train = df_train[~df_train['body'].isin(['[deleted]', '[removed]'])]
# Store it in pickle
if not os.path.exists('./data/train_data.pickle'):
    with open('./data/train_data.pickle', 'wb') as handle:
        pickle.dump(df_train, handle, protocol=pickle.HIGHEST_PROTOCOL)