import pickle
import pandas as pd
import matplotlib.pyplot as plt
import  re

with open('data/gameswap_history.pickle', 'rb') as f:
    gameswap = pickle.load(f)
with open('data/gamesale_history.pickle', 'rb') as f:
    gamesale = pickle.load(f)
with open('data/mushroomkingdom_history.pickle', 'rb') as f:
    mushroomkingdom = pickle.load(f)

game_total = pd.concat([gameswap,gamesale], axis=0)

# Select the rows where author is not '[deleted]' or '[removed]'
# game_total = game_total[~game_total['author'].isin(['[deleted]', '[removed]'])]
# Select the rows where reply_author is not '[deleted]' or '[removed]'
# game_total = game_total[~game_total['reply_author'].isin(['[deleted]', '[removed]'])]
# Select the rows where author and reply_author are not nan
# game_total = game_total[~game_total['author'].isnull()]
# game_total = game_total[~game_total['reply_author'].isnull()]

# Choose author = 'SwapNSalebot' from game_total
# game_bot = game_total[game_total['author'] == 'SwapNSalebot']

# game_prior_bot = game_total.loc[game_total['created_utc']<="2019-12-01"]


# west = game_total.loc[game_total['author'] == 'westcoaststyle']
#
#
# text = 'Successful trade with u/WickedRoot-__. Swapped my digital Halo MCC for his digital Forza 5'
# match = re.search(r'(?<=u/)[\w\-\_]+', text)
# match.group(0)

pattern = r'^(.*)_(?!.*_)'
# apply the pattern to the column 'index'
game_total['user'] = game_total['index'].apply(lambda x: re.search(pattern, x).group(1))
# put the user column to the front
cols = game_total.columns.tolist()
cols = cols[-1:] + cols[:-1]
game_total = game_total[cols]
# Get the rows with user = None
# check= game_total[game_total['user']=='none']

# Choose the rows where user is not 'none'
game_total = game_total[game_total['user'] != 'none']

# Create subdataframe for each year using the 'created_utc' column from year 2013 to 2020
game_2013 = game_total.loc[game_total['created_utc']<="2013-12-31"]
game_2014 = game_total.loc[(game_total['created_utc']>="2014-01-01") & (game_total['created_utc']<="2014-12-31")]
game_2015 = game_total.loc[(game_total['created_utc']>="2015-01-01") & (game_total['created_utc']<="2015-12-31")]
game_2016 = game_total.loc[(game_total['created_utc']>="2016-01-01") & (game_total['created_utc']<="2016-12-31")]
game_2017 = game_total.loc[(game_total['created_utc']>="2017-01-01") & (game_total['created_utc']<="2017-12-31")]
game_2018 = game_total.loc[(game_total['created_utc']>="2018-01-01") & (game_total['created_utc']<="2018-12-31")]
game_2019 = game_total.loc[(game_total['created_utc']>="2019-01-01") & (game_total['created_utc']<="2019-12-31")]
game_2020 = game_total.loc[(game_total['created_utc']>="2020-01-01") & (game_total['created_utc']<="2020-12-31")]
game_2021 = game_total.loc[(game_total['created_utc']>="2021-01-01") & (game_total['created_utc']<="2021-03-31")]
game_years = [game_2013, game_2014, game_2015, game_2016, game_2017, game_2018, game_2019, game_2020, game_2021]

# Plot these subdataframes, group by user and 'subreddit' and count the number of rows.
# In a plot, plot these subdataframes in a line plot
# Plot the distribution of gameswap and gamesale in each year
plt.clf()
fig, ax = plt.subplots(3, 3, figsize=(20, 10))
for year, game_year in enumerate(game_years):
    to_plot = game_year.groupby(['user', 'subreddit']).size().unstack().fillna(0)
    # Plot the distribution of gameswap and set alpha to 0.5 ,plot the distribution of gamesale and set alpha to 1 in the same plot.
    to_plot.plot(kind='hist', stacked=True, ax=ax[year//3, year%3],logy=True)
    # legend
    ax[year//3, year%3].legend()
    # title
    ax[year//3, year%3].set_title('Year {}'.format(2013+year))
    # x label
    ax[year//3, year%3].set_xlabel('Number of transactions')
plt.tight_layout()
plt.show()

