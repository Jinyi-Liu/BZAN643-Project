import pandas as pd
import pickle
import numpy as np

# Load the gameswap transaction data with col names ['user1','game1','user2','game2']
pair = pd.read_csv('data/pairs.csv', names=['user1','game1','user2','game2'])
# Load have and wish data
have = pd.read_csv('data/have.csv', names=['user','game'])
wish = pd.read_csv('data/wish_dense.csv', names=['user','game'])

# Load the games data we get from IGDB
games = pd.read_csv('data/games_tbp.csv', index_col=0)
# Add a column of index with name 'game_id', second column
games.insert(1, 'game_id', range(0, len(games)))

games_genres = games[['game_id', 'genres']]

# Join the pair and games_genres on game1
pair_genres = pair.join(games_genres.set_index('game_id'), on='game1')
# Join the pair_genres and games_genres on game2
pair_genres = pair_genres.join(games_genres.set_index('game_id'), on='game2', rsuffix='_2')

relationship = pair_genres[['genres', 'genres_2']]
# Drop the rows with NaN
relationship = relationship.dropna()
# Transform the columns to list
relationship['genres'] = relationship['genres'].apply(lambda x: [int(y) for y in x[1:-1].split(',')])
relationship['genres_2'] = relationship['genres_2'].apply(lambda x: [int(y) for y in x[1:-1].split(',')])


relationship_explode = relationship.explode(['genres'])
relationship_explode = relationship_explode.explode(['genres_2'])
relationship_explode = relationship_explode.groupby(['genres', 'genres_2']).size().reset_index(name='count')

# If genres_2 is greater than genres, swap them
relationship_explode['genres'], relationship_explode['genres_2'] = \
    zip(*relationship_explode.apply(lambda x: (x['genres_2'], x['genres']) if x['genres_2'] > x['genres'] else (x['genres'], x['genres_2']), axis=1))

# Sort the values by genres and genres_2
relationship_explode = relationship_explode.sort_values(by=['genres', 'genres_2'])

# Group by genres and genres_2 and sum the count
relationship_explode = relationship_explode.groupby(['genres', 'genres_2']).sum().reset_index()

with open('data/genres_igdb.pickle','rb') as f:
    genres_names = pickle.load(f)[['id','name']]

df = pd.merge(relationship_explode, genres_names, left_on='genres',right_on='id')
relationship_genres = pd.merge(df, genres_names, left_on='genres_2',right_on='id',suffixes=['_1','_2'])[['name_1','name_2','count']]
relationship_syn = relationship_genres.pivot('name_1','name_2','count')
# Make the relationship symmetric without changing the diagonal
relationship_syn = relationship_syn.fillna(0) + relationship_syn.T.fillna(0)
# Divide the diagonal by 2
np.fill_diagonal(relationship_syn.values, relationship_syn.values.diagonal()/2)
# Delete the rows and columns with all NaN
relationship_syn = relationship_syn.dropna(axis=0, how='all')
relationship_syn = relationship_syn.dropna(axis=1, how='all')


# Plot the relationship between genres
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# Set the figure size
plt.figure(figsize=(20,20))
# Plot the relationship_genres symmetrically
# Annotate the heatmap with the count, not scientific notation
ax = sns.heatmap(relationship_syn, annot=True, fmt='g', cmap='Blues')
# Set the title
plt.title('Relationship between genres')
# Set the x-axis label
plt.xlabel('Genres')
# Let the x-axis in the upper side
ax.xaxis.tick_top()
# Rotate the x-axis label
plt.xticks(rotation=45, ha='left')
# Set the y-axis label
plt.ylabel('Genres')
plt.yticks(rotation=0)
# Save the figure
plt.show()
