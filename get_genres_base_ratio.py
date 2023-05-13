import pandas as pd
import pickle
with open('./data/games.pkl', 'rb') as handle:
    df_games = pd.DataFrame.from_dict(pickle.load(handle))
    
total_genres = {}
for genres_list in df_games['genres']:
    try:
        for genres in genres_list:
            # calculate the total number of each genre.
            total_genres[genres] = total_genres.get(genres, 0)+1
    except:
        pass
df_total_genres = pd.DataFrame.from_dict(total_genres, orient='index')

with open('data/genres_igdb.pkl','rb') as f:
    genres_names = pickle.load(f)[['id','name']]
    
df_total  = df_total_genres.join(genres_names.set_index('id'), how='left').sort_values(0, ascending=False).sort_index()
df_total.columns = ['count', 'name']
df_total['percent'] = df_total['count']/df_total['count'].sum()*100
total_genres_count = df_total.sort_values('name')


# Get console games genres base ratio.
with open('data/platforms.pkl', 'rb') as handle:
    platforms = pickle.load(handle)
    
df_platforms = pd.DataFrame.from_dict(platforms)
console_platforms = df_platforms[df_platforms['category'].isin([1,5])]
console_platform_id = list(console_platforms.id)

df_games['platforms'].fillna('None', inplace=True)
console_game = df_games[df_games['platforms'].apply(lambda x: any([True if i in console_platform_id else False for i in x]))]

console_genres = {}
for genres_list in console_game['genres']:
    try:
        for genres in genres_list:
            # calculate the total number of each genre.
            console_genres[genres] = console_genres.get(genres, 0)+1
    except:
        pass
    
df_console_genres = pd.DataFrame.from_dict(console_genres, orient='index')

df_console_genres_count = df_console_genres.join(genres_names.set_index('id'), how='left').sort_values(0, ascending=False).sort_index()
df_console_genres_count.columns = ['count', 'name']
df_console_genres_count['percent'] = df_console_genres_count['count']/df_console_genres_count['count'].sum()*100

df_console_genres_count.sort_values('name', inplace=True)

total_genres_count.join(df_console_genres_count, lsuffix='_total', rsuffix='_console').sort_values('name_total').to_pickle('./data/genres_count_total.pkl')


df_console_genres_count[['name','count','percent']].to_pickle('data/console_genres_count.pkl')