import multiprocessing
import time
import pickle
import requests
from time import sleep


# Get the comment using crawler
def get_comment(url, bot_name_to_crawl='my bot 3.1415', redirect_dict=None):
    # Get the redirect url already get
    if redirect_dict is None:
        redirect_dict = {}
    else:
        redirect_dict = redirect_dict

    # Check the url if it's a short url like redd*
    if url.startswith('redd'):
        long_url_got = redirect_dict.get(url)
        if long_url_got is None:
            short_url = 'https://' + url
            # Get the redirect long url.
            long_url = requests.get(short_url, headers={'User-agent': bot_name_to_crawl}, allow_redirects=True).url
            redirect_dict[url] = long_url
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


redirect_dict = {}
error_dict = []

def process_value(key, value, i, redirect_dict, error_dict):
    if value.get('comment') is None:
        try:
            value['comment'] = get_comment(value['link'], redirect_dict = redirect_dict)
        except Exception as e:
            print(e)
            # Change the bot name after a while.
            try:
                value['comment'] = get_comment(value['link'], 'my bot %d' % i, redirect_dict = redirect_dict)
            except Exception as e:
                print(e)
                error_dict.append({key: value})
                value['comment'] = 'error'  # If the comment is not get, set it to error.
        return value
    else:
        return value

def main():
    redirect_dict = {}
    error_dict = []
    start_time = time.time()
    i = 0
    with open('./data/transformed_data_temp_multi.pickle', 'rb') as handle:
        transformed_history = pickle.load(handle)
    # Use multiprocessing to speed up
    # Store error_dict and redirect_dict to avoid repeat
    with multiprocessing.Pool(20) as pool:
        for key, value_list in transformed_history.items():
            value_list = pool.starmap(process_value, [(key, value, i, redirect_dict, error_dict) for value in value_list])
            transformed_history[key] = value_list
            i += 1
            if i % 100 == 0:
                with open('./data/transformed_data_temp_multi_test.pickle', 'wb') as handle:
                    pickle.dump(transformed_history, handle, protocol=pickle.HIGHEST_PROTOCOL)
                print(i, time.time() - start_time)
    # with open('./data/transformed_data_temp_multi.pickle', 'wb') as handle:
    #     pickle.dump(transformed_history, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # with open('./data/redirect_dict.pickle', 'wb') as handle:
    #     pickle.dump(redirect_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # with open('./data/error_dict.pickle', 'wb') as handle:
    #     pickle.dump(error_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('done')
if __name__ == '__main__':
    main()
