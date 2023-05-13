import pandas as pd
import numpy as np
import pickle
import os

# Calculate the similarity between the names
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Get the most similar between the df_reddit and the df by multiprocessing
from multiprocessing import Pool
from functools import partial

def get_most_similar(_df_reddit, _df, column):
    # Get the most similar
    most_similar = process.extract(_df_reddit, _df[column], limit=1, scorer=fuzz.ratio)
    # Get the similarity
    similarity = most_similar[0][1]
    # Get the name
    name = most_similar[0][0]
    # Get the index
    index = df[df[column]==name].index[0]
    return similarity, index


if not os.path.exists('./data/games_tbp.csv'):
    # This dataset contains all the games we get from IGDB.
    with open('data/games.pkl', 'rb') as f:
        games_list = pickle.load(f)

    df = pd.DataFrame.from_dict(games_list)
    df['first_release_date'] = pd.to_datetime(df['first_release_date'], unit='s')

    # Let the id be the index
    df.set_index('id', inplace=True)
    # Let the name be the first column
    df = df[['name','genres','game_modes'] + [col for col in df.columns if col != 'name']]

    # Drop the created_at, screenshots, url, websites, check_sum
    df.drop(['created_at','screenshots','url','websites','updated_at'], axis=1, inplace=True)

    # df reddit
    # Get the game names from Rappaz et al. (2017)'s dataset.
    with open('./data/game_names.csv','r') as f:
        game_names = [line[:-2] for line in f.readlines()]
    # Transform the list into a dataframe
    df_reddit = pd.DataFrame(game_names, columns=['reddit_name'])
    
    # Get the most similar
    with Pool(20) as p:
        base_similarity = p.map(partial(get_most_similar, _df=df, column='name'), df_reddit['reddit_name'])
    # Save the base_similarity
    with open('./data/base_similarity.pkl','wb') as f:
        pickle.dump(base_similarity, f)


    # Join the similarity with the df_reddit
    df_reddit['similarity'] = [sim[0] for sim in base_similarity]
    df_reddit['index'] = [sim[1] for sim in base_similarity]

    # Join the df_reddit with the df by the index
    df_test = df_reddit.join(df, on='index')

    df_reddit_new = pd.DataFrame(game_names, columns=['reddit_name'])
    df_reddit_new['similarity'] = [sim[0] for sim in base_similarity]
    df_reddit_new['index'] = [sim[1] for sim in base_similarity]
    # Join by the index of df_reddit_new and df.index
    df_test = df_reddit_new.join(df, on='index')
    df_test.to_csv('./data/games_tbp.csv')
    print("Match dataset created.")
else:
    print("Dataset already exists.")