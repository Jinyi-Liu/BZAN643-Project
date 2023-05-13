import requests
import re
import pickle
import os
from time import sleep
from bs4 import BeautifulSoup as bs


if not os.path.exists('./data/gameswap_member.pkl'):
    if not os.path.exists('./data/archive_url_list_swap.pkl'):
        base_url = "http://archive.org/wayback/available?url=https://www.reddit.com/r/gameswap?timestamp="
        # Get a list month by month from 2009 to 2023 with the format of YYYYMMDD
        month_list = [str(year) + str(month).zfill(2) + '01' for year in range(2009, 2024) for month in range(1, 13)]

        base = "http://web.archive.org/web/%s000000id_/https://www.reddit.com/r/gameswap/"
        archive_url_list = []
        for month in month_list:
            # Get the html
            print(month)
            html = requests.get(base % month).url
            print(html)
            archive_url_list.append(html)
            sleep(0.2)
        # Get the unique url in archive_url_list
        archive_url_list = list(set(archive_url_list))
        # Save the archive_url_list using pickle
        with open('./data/archive_url_list_swap.pkl', 'wb') as f:
            pickle.dump(archive_url_list, f)
    else:
        with open('./data/archive_url_list_swap.pkl', 'rb') as f:
            archive_url_list = pickle.load(f)

    if not os.path.exists('./data/archive_html_list_swap.pkl'):
        # Get the html from archive_url_list
        archive_html_list = []
        for archive_url in archive_url_list:
            print(archive_url)
            archive_html_list.append(requests.get(archive_url).text)
            sleep(0.2)
        # Save the archive_html_list using pickle
        with open('./data/archive_html_list_swap.pkl', 'wb') as f:
            pickle.dump(archive_html_list, f)
    else:
        with open('./data/archive_html_list_swap.pkl', 'rb') as f:
            archive_html_list = pickle.load(f)

    # Sort the archive_html_list by the date
    archive_html_list = [x for _, x in sorted(zip(archive_url_list, archive_html_list))]
    archive_url_list.sort()

    # Get the YYYYMMDD from the archive_url_list
    date = [re.findall(r'\d{8}', x)[0] for x in archive_url_list]

    # # Get the max from the values
    # members = [x if x is not None else ['0'] for x in temp.values()]
    #
    # # Replace , by '' for all the string in the sublist and convert to int
    # members = [[int(x.replace(',', '')) for x in sublist] for sublist in members]
    #
    # # Get the max from the sublist
    # max_members = [max(sublist) for sublist in members]
    #
    max_members = [228,321,410,592,824,
           1190,1885,6894,7122,7089,
           7146,7615,7925,8661,8963,
           9290,9498,10032,10071,10293,
           11814,12024,12546,12762,13047,
           13102,13257,13603,13963,14556,
           14732,14930,15064,15124,15592,
           15920,16060,16478,16680,16826,
           17047,17313,17587,17624,17076,
           17261,None,17567,17659,18001,
           18220,19282,19299,19515,19768,
           24803,25113,25863,27572,29167,
           29667,30701,30918,32071,33352,
           34374,35842,36580,37340,38396,
           39490,40222,44700,45200,46300,
           46900,47600,48200,48800,49300,
           49800,49900,51100,51200,51400,
           52000,52300,52500,53043,56763,
           57727,57896,58165,58338,58600,
           58800,59000,59156,59400,59764,
           60100,60300
          ]
    date_members = list(zip(date, max_members))
    # date_members to dict
    date_members = dict(date_members)
    date_members.pop('20160301') # None in this date.

    # Save date_members to pickle
    with open('./data/gameswap_member.pkl', 'wb') as f:
        pickle.dump(date_members, f)
else:
    pass
