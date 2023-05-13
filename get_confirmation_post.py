import multiprocessing
import time
import pickle
import requests
from time import sleep
import concurrent.futures
import os
from bs4 import BeautifulSoup as bs
import re
import random


def get_permalink(url):
    if url[:8] == 'https://':
        short_url = url
    else:
        short_url = 'https://' + url
    # Get the redirect page.
    page = requests.get(short_url, headers={'User-agent': "%.4f" % random.random()}, allow_redirects=True)
    soup = bs(page.text, 'html.parser')
    # Get the permalink from the redirect html page.
    permalink = soup.find('shreddit-redirect').get('href')
    sleep(0.1)
    return permalink

# Get the comment using crawler
def get_comment(url, bot_name_to_crawl='my bot 0210', redirect_dict=None):
    # Get the redirect url already get
    if redirect_dict is None:
        redirect_dict = {}
    else:
        redirect_dict = redirect_dict

    # Check the url if it's a short url like redd*
    if not url.startswith('https://'):
        long_url_got = redirect_dict.get(url)
        if long_url_got is None:
            permalink = get_permalink(url)
            real_url = 'https://www.reddit.com' + permalink
            redirect_dict[url] = real_url
        else:
            long_url = long_url_got
        url = long_url

    json_raw = requests.get(url + '.json', headers={'User-agent': bot_name_to_crawl})
    try:
        # standard form of the comment json
        _comment = json_raw.json()[1]['data']['children'][0]['data']
        sleep(0.10)
        return _comment,
    except Exception as e:
        return 'error'


def process_value(key, value_list, i, redirect_dict, error_dict):
    for value in value_list:
        if value.get('comment') is None:
            try:
                value['comment'] = get_comment(value['link'], redirect_dict=redirect_dict)
            except Exception as e:
                print(e)
                # Change the bot name after a while.
                try:
                    value['comment'] = get_comment(value['link'], 'my bot %d' % i, redirect_dict=redirect_dict)
                except Exception as e:
                    print(e)
                    error_dict.append({key: value})
                    value['comment'] = 'error'  # If the comment is not get, set it to error.
    return key, value_list

# Split by first - and return a tuple
def split_by_dash(string):
        return tuple(string.split(' - ', 1))
    
def main():
    if not os.path.exists('./data/redirect_dict.pkl'):
        redirect_dict = {}
    else:
        with open('./data/redirect_dict.pkl', 'rb') as handle:
            redirect_dict = pickle.load(handle)
    error_dict = []
    start_time = time.time()
    i = 0
    
    # Load the raw history data from pickle.
    # https://raw.githubusercontent.com/RegExrTech/SwapBot/master/database/gamesale-swaps.json
    with open('./data/history.pkl', 'rb') as handle:
        history = pickle.load(handle)

    if not os.path.exists('./data/transformed_history.pkl'):
        # Processed data
        pattern = r"/r/(\w+)/"
        transformed_history = {}
        wrong_data = {}
        for key, value_list in history.items():
            for value in value_list:
                try:
                    user, link = split_by_dash(value)
                    # Use re to get the string between "r/" and "/" in the link
                    try:
                        _type = re.search(pattern, link).group(1)
                    except AttributeError:
                        _type = 'tbd'
                        
                    transformed_history.setdefault(key, []).append({
                            'user': user,
                            'link': link,
                            'type': _type
                        })
                except ValueError:
                    wrong_data.setdefault(key, []).append(value)
        with open('data/transformed_history.pkl', 'wb') as f:
            pickle.dump(transformed_history, f)
    else:
        with open('data/transformed_history.pkl', 'rb') as f:
            transformed_history = pickle.load(f)
            
    if not os.path.exists('./data/transformed_data.pkl'):
        with concurrent.futures.ProcessPoolExecutor(max_workers=20) as executor:
            futures = []
            for key, value_list in list(transformed_history.items()):
                i += 1
                future = executor.submit(process_value, key, value_list, i, redirect_dict, error_dict)
                futures.append((key, future))
                if i % 500 == 0:
                    # Wait for all submitted futures to complete before writing to file
                    for k, f in futures:
                        k, value_list = f.result()
                        transformed_history[k] = value_list
                    with open('./data/transformed_data.pkl', 'wb') as handle:
                        pickle.dump(transformed_history, handle, protocol=pickle.HIGHEST_PROTOCOL)
                    print(i)
                    print('time used: %f' % (time.time() - start_time))
                    futures = []

            # Wait for any remaining futures to complete
            for k, f in futures:
                k, value_list = f.result()
                transformed_history[k] = value_list
                
            tbd_none = {}
            tbd_error = {}
            for key, value_list in transformed_history.items():
                for value in value_list:
                    if not value.get('comment'):
                        tbd_none.setdefault(key, []).append(value)
                    elif value['comment'] == 'error':
                        tbd_error.setdefault(key, []).append(value)
                        # Drop the error
                        print(value)
                        transformed_history[key].remove(value)
                        
            with open('./data/transformed_data.pkl', 'wb') as handle:
                pickle.dump(transformed_history, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open('./data/error_tbp.pkl', 'wb') as handle:
            pickle.dump(tbd_error, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    print('done')
if __name__ == '__main__':
    main()
