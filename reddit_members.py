import requests
import re
import pickle

# Get the url from gameswap_history.txt
with open('gameswap_history.txt', 'r') as f:
    url = f.readlines()

base_url = "http://archive.org/wayback/available?url=https://www.reddit.com/r/gameswap?timestamp="
# Get a list month by month from 2009 to 2023 with the format of YYYYMMDD
month_list = [str(year) + str(month).zfill(2) + '01' for year in range(2009, 2024) for month in range(1, 13)]

base = "http://web.archive.org/web/%s000000id_/https://www.reddit.com/r/gameswap/"
archive_url_list = []
for month in month_list:
    # Get the html
    print(month)
    html = requests.get(base%month).url
    print(html)
    archive_url_list.append(html)

# Get the unique url in archive_url_list
archive_url_list = list(set(archive_url_list))

# Get the html from archive_url_list
archive_html_list = []
for archive_url in archive_url_list:
    print(archive_url)
    archive_html_list.append(requests.get(archive_url).text)

# Sort the archive_html_list by the date
archive_html_list = [x for _, x in sorted(zip(archive_url_list, archive_html_list))]
archive_url_list.sort()

# Get the YYYYMMDD from the archive_url_list
date = [re.findall(r'\d{8}', x)[0] for x in archive_url_list]


# Get the max from the values
members = [x if x is not None else ['0'] for x in temp.values() ]

# Replace , by '' for all the string in the sublist and convert to int
members = [[int(x.replace(',', '')) for x in sublist] for sublist in members]
# Get the max from the sublist
max_members = [max(sublist) for sublist in members]


date_members = list(zip(date, max_members))
# Save the date_members using pickle
with open('data/date_members.pickle', 'wb') as f:
    pickle.dump(date_members, f)

# Get the date and max_members from the date_members where the max_members is 0
b=[x for x in date_members if x[1] == 0]
a = [0, 29167, 29667,30918,32071,33352,34374,35842,37340,38396,39490,40222,44700,45200,46300,46900,47600,48200,48800,49300]+[49800,49900,51100,51200,51400,52000,52300,52500,58600,58800,59000,59400,60100]

adict = {}

# date_members to dict
date_members = dict(date_members)
for dm, num in zip(b, a):
    date_members[dm[0]] = num
date_members.pop('20160301')

# Save date_members to pickle
with open('data/date_members_dict_processed.pickle', 'wb') as f:
    pickle.dump(date_members, f)

# Load date_members from pickle
with open('data/date_members_dict_processed.pickle', 'rb') as f:
    date_members = pickle.load(f)

# Plot date_members, the x-axis is the date and the y-axis is the max_members
# Tick by month
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import seaborn as sns
import numpy as np

# Get the date and max_members from the date_members
date = [datetime.datetime.strptime(x[0], '%Y%m%d') for x in date_members.items()]
max_members = [x[1] for x in date_members.items()]

# Plot the date and max_members
fig, ax = plt.subplots(figsize=(20, 10))
ax.plot(date, max_members)
ax.set_title('Number of members in gameswap')
ax.set_xlabel('Date')
ax.set_ylabel('Number of members')
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45)
# plt.savefig('date_members.png')

plt.show()