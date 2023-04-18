import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import pickle
import seaborn as sns
import numpy as np
import pandas as pd

with open('data/date_members_dict_processed.pickle', 'rb') as f:
    date_members_swap = pickle.load(f)

with open('data/gamesale.pickle', 'rb') as f:
    date_members_sale = pickle.load(f)

# Load the console_date from csv
console_date = pd.read_csv('data/console_date.csv', index_col=0)
# Change the date to %Y%m%d
console_date['date'] = [x.replace('-', '') for x in console_date['date']]

# Plot date_members_swap and date_members_sale, the x-axis is the date and the y-axis is the max_members
# Tick by month
# Mark the console  date
# Set the figure size

plt.figure(figsize=(20, 10))
# Plot the date and max_members
plt.plot([datetime.datetime.strptime(x[0], '%Y%m%d') for x in date_members_swap.items()], [x[1] for x in date_members_swap.items()], label='GameSwap')
plt.plot([datetime.datetime.strptime(x[0], '%Y%m%d') for x in date_members_sale.items()], [x[1] for x in date_members_sale.items()], label='GameSale')
# Mark the console date
for i in range(len(console_date)):
    plt.axvline(x=datetime.datetime.strptime(console_date['date'][i], '%Y%m%d'), color='r', linestyle='--')
    plt.text(datetime.datetime.strptime(console_date['date'][i], '%Y%m%d'), 0, console_date.index[i], rotation=90)
# Set the title
plt.title('Number of members in gameswap and gamesale')
# Set the x-axis label and rotate the label
plt.xlabel('Date')
plt.xticks(rotation=45)
# Set the y-axis label
plt.ylabel('Number of members')
# Set the x-axis tick by month
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
# Set the legend to the upper left
plt.legend(loc='upper left')
# No grid
plt.grid(False)
# Save the figure
plt.savefig('plot/swap_sale_console_release.png')
# Show the figure
plt.show()