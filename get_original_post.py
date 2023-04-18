import pandas as pd
import requests
from time import sleep
import pickle
import os

data = pd.read_pickle("./data/df.pickle")

# data.head()
# Get url from body starting with 'www.reddit.com' or 'www.reddit.com'
pattern = r"(r/(\w+)/comments/(\w+))"

# Get the url from body
data['url'] = data['body'].str.extract(pattern, expand=False)[0]

time = '2018-12-31'
# Choose the rows before time
data = data[data['created_utc'] <= time]

# Select the rows with url!=nan
# It only contains 2000 rows, so we just ignore the rows with url=nan.
# check = data[data['url'].isna()]
data = data[~data['url'].isna()] # Choose the rows with url!=nan

# Get the comment using crawler
def get_json(index, url):
    print(index)
    try:
        json_raw = requests.get("http://www.reddit.com/"+ url + '.json', headers={'User-agent': "my bot %d"%index})
    except Exception:
        return index, None
    sleep(0.05)
    return index, json_raw.json()



# Get the json from url, and save it in a dictionary, key is the index column
# Use multi-threading to speed up the process
if not os.path.exists('./data/original_post.pickle'):
    original_post = {}
    from multiprocessing.dummy import Pool as ThreadPool
    pool = ThreadPool(20)
    results = pool.starmap(get_json, [(index, url) for index, url in data['url'].iteritems()])
    pool.close()
    pool.join()

    # Check if there is any error
    for index, json in results:
        if json is not None:
            original_post[index] = json

    # Check if error
    # About 10 rows return 404 or 403, so we just ignore them.
    # These rows can be retrieved by comparing dataframe and the dictionary.
    for index, json in results:
        if type(json) is not list:
            # print( get_json(index, data['url'][index])[1] )
            original_post.pop(index, None)

    # Save the dictionary
    with open('./data/original_post.pickle', 'wb') as handle:
        pickle.dump(original_post, handle, protocol=pickle.HIGHEST_PROTOCOL)
else:
    with open('./data/original_post.pickle', 'rb') as handle:
        original_post = pickle.load(handle)

valid_original_post_index = list(original_post)
data = data[data.index.isin(valid_original_post_index)]
def get_created_utc(json_item):
    return json_item[0]['data']['children'][0]['data']['created_utc']

# Get the created_utc from json, add it to the dataframe
data['created_utc_original'] = data.index.map(lambda x: get_created_utc(original_post[x]))
# Transform the created_utc to datetime
data['created_utc_original'] = pd.to_datetime(data['created_utc_original'], unit='s')

# Save the dataframe
# data.to_pickle("./data/df_pre2019_original.pickle")
with open('./data/df_pre2019_original.pickle', 'rb') as handle:
    data = pickle.load(handle)

data['confirmed_time'] = data['created_utc'] - data['created_utc_original']
# Delete the rows with confirmed_time < 0. Outliers. Two rows.
data = data[data['confirmed_time'] >= pd.Timedelta(0)]

# Get the confirmed_time summary, grouping by type.
confirmed_time_summary = data.groupby('type')['confirmed_time'].describe()

# Plot the data['confirmed_time'] day distribution by type gamesale and gameswap.
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
data['confirmed_time'].dt.days.hist(by=data['type'], bins=100)
plt.show()

# pd one day
