import requests
from bs4 import BeautifulSoup as bs
import re
import os
import pickle
from time import sleep


if not os.path.exists('./data/gamesale_member.pkl'):
# Create a list month by month from 2013 to 2023 with the format of YYYYMMDD
    if not os.path.exists('./data/archive_url_list_sale.pkl'):
        month_list = [str(year) + str(month).zfill(2) + '01' for year in range(2012, 2024) for month in range(1, 13)][11:-9]

        base = "http://web.archive.org/web/%s000000id_/https://www.reddit.com/r/gamesale/"
        archive_url_list = []
        for month in month_list:
            # Get the html
            print(month)
            html = requests.get(base % month).url
            print(html)
            archive_url_list.append(html)
            sleep(0.2)

        # Get the unique url in archive_url_list
        archive_url_list = sorted(list(set(archive_url_list)))
    else:
        with open('./data/archive_url_list_sale.pkl', 'rb') as f:
            archive_url_list = pickle.load(f)
    
    if not os.path.exists('./data/archive_html_list_sale.pkl'):
        # Get the html from archive_url_list
        archive_html_list = []
        for archive_url in archive_url_list:
            print(archive_url)
            archive_html_list.append(requests.get(archive_url).text)
            sleep(0.2)

        # Save the archive_html_list using pickle
        with open('./data/archive_html_list_sale.pkl', 'wb') as f:
            pickle.dump(archive_html_list, f)
    else:
        with open('./data/archive_html_list_sale.pkl', 'rb') as f:
            archive_html_list = pickle.load(f)

    # Parse the archive_html_list with bs4
    archive_html_list = [bs(x, 'html.parser') for x in archive_html_list]

    # Get the number in the class number
    temp = [x.find_all('span', class_='number') for x in archive_html_list]

    # Find the number like 10.1k
    pattern = r"\d+(?:\.\d+)?k\\n"
    store = []
    for html in archive_html_list[28:]:
        matches = re.findall(pattern, str(html.prettify ("utf-8")))
        store.append(matches)

    for i in range(len(store)):
        if len(store[i]) == 0:
            store[i] = [0]
        else:
            store[i] = [int(float(x.replace('k\\n', ''))*1000) for x in store[i]]

    # Get number from temp list
    pattern = r"\d+(?:\,\d+)?"
    num_list = []
    for x in temp[:28]:
        matches = re.findall(pattern, str(x))
        num_list.append(matches[0])
    # Replace , by '' for all the string in the sublist and convert to int
    num_list = [int(x.replace(',', '')) for x in num_list]

    total_members = num_list+ [x[0] for x in store]

    # Get the YYYYMMDD from the archive_url_list
    date = [re.findall(r'\d{8}', x)[0] for x in archive_url_list]
    date_members = list(zip(date, total_members))
    date_members_dict = dict(date_members)

    # Drop the values that are 0
    date_members_dict = {k: v for k, v in date_members_dict.items() if v != 0}

    # Save the transformed_data using pickle
    with open('./data/gamesale_member.pkl', 'wb') as f:
        pickle.dump(date_members_dict, f)
else:
    pass