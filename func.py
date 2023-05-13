import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def flatten_history_to_df(transformed_data):
    # For each comment, we want the following information:
    # - author
    # - body
    # - created_utc
    # - permalink
    # - replies['data']['children'][0]['data']
    keys = ['author', 'body', 'created_utc', 'permalink']
    reply_keys = ['author', 'body']
    stop = False
    simplified_data = {}
    for key, value_list in transformed_data.items():
        for value in value_list:
            if value.get('comment') != 'error':
                try:
                    if type(value['comment']) == tuple:
                        value['comment'] = value['comment'][0]
                        
                    simplified_data.setdefault(key, []).append({k: value['comment'][k] for k in keys})
                except Exception as e:
                    print(e)
                try:
                    if value['comment']['replies'] != '':
                        reply = value['comment']['replies']['data']['children'][0]['data']
                    else:
                        reply['author'] = value['user']
                        reply['body'] = ''
                    for reply_key in reply_keys:
                        if reply.get(reply_key) is not None:
                            simplified_data[key][-1].setdefault('reply_%s' % reply_key,  reply[reply_key])
                except Exception as e:
                    print(e)
            else:
                simplified_data.setdefault(key, []).append(value)

    flatten_dict = {}
    for key, value_list in simplified_data.items():
        for index, value in enumerate(value_list):
            flatten_dict.setdefault(key+"_%d" % index,value)
    return pd.DataFrame(flatten_dict).T.reset_index()


def get_relationship(pair, games_genres, have_wish=False):
    '''
    have_with is a boolean value. If it is True, we don't need to swap the genres and genres_2 as the relationship is not symmetric.
    '''
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


    if not have_wish:
        # If genres_2 is greater than genres, swap them
        relationship_explode['genres'], relationship_explode['genres_2'] = \
            zip(*relationship_explode.apply(lambda x: 
                (x['genres_2'], x['genres']) if 
                    x['genres_2'] > x['genres'] else 
                (x['genres'], x['genres_2']), axis=1))

        # Sort the values by genres and genres_2
        relationship_explode = relationship_explode.sort_values(by=['genres', 'genres_2'])
    
    # Group by genres and genres_2 and sum the count
    relationship_explode = relationship_explode.groupby(['genres', 'genres_2']).sum().reset_index()
    
    return relationship_explode

def relationship_with_name(relationship_explode, genres_names, have_wish=False):
    df = pd.merge(relationship_explode, genres_names, left_on='genres',right_on='id')
    relationship_genres = pd.merge(df, genres_names, left_on='genres_2',right_on='id',suffixes=['_1','_2'])[['name_1','name_2','count']]
    relationship_syn = relationship_genres.pivot('name_1','name_2','count')

    if not have_wish:
        # Make the relationship symmetric without changing the diagonal
        relationship_syn = relationship_syn.reindex(index=relationship_syn.index, columns=relationship_syn.index).fillna(0) + relationship_syn.reindex(index=relationship_syn.index, columns=relationship_syn.index).fillna(0).T

        # Divide the diagonal by 2
        np.fill_diagonal(relationship_syn.values, relationship_syn.values.diagonal()/2)
        

    # Delete the rows and columns with all NaN
    relationship_syn = relationship_syn.dropna(axis=0, how='all')
    relationship_syn = relationship_syn.dropna(axis=1, how='all')
    relationship_syn = relationship_syn.fillna(0)
    return relationship_syn


def plot_relationship(relationship_explode, figure_name, genres_names, processed=False, have_wish=False):
    if not processed:
        # i.e., not ``exploded''
        relationship_syn = relationship_with_name(relationship_explode, genres_names, have_wish)
    else:
        relationship_syn = relationship_explode
    # Set the figure size
    plt.figure(figsize=(20,20))
    # Plot the relationship_genres symmetrically
    # Annotate the heatmap with the count, not scientific notation
    ax = sns.heatmap(relationship_syn, annot=True, fmt='g', cmap='coolwarm',center=0)
    # Set the title
    plt.title('Relationship between genres')
    if not have_wish:
        # Set the x-axis label
        plt.xlabel('Genres', fontsize=20)
        # Set the y-axis label
        plt.ylabel('Genres', fontsize=20)
    else:
        plt.xlabel('Genres Wish', fontsize=20)
        plt.ylabel('Genres Have', fontsize=20)
    # Let the x-axis in the upper side
    ax.xaxis.tick_top()
    # Rotate the x-axis label
    plt.xticks(rotation=45, ha='left')
    
    plt.yticks(rotation=0)
    # Save the figure
    plt.savefig('./plot/relationship_%s.png'%figure_name, dpi=300, bbox_inches='tight', transparent=True)
    plt.show()
    
import scipy.stats
def plot_relationship_with_t(relationship_diff, figure_name, genres_names, save=False):
    t_value = lambda x: (x-x.mean())/x.std()
    t_value_matrix = relationship_diff.apply(t_value, axis=1)
    degree_of_freedom = len(relationship_diff.columns)-1
    t_crit = scipy.stats.t.ppf(1-np.array([0.20,0.10,0.05])/2, degree_of_freedom)
    plt.figure(figsize=(10,9))
    # Plot relationship_diff in a heatmap, star the significant values
    ax = sns.heatmap(relationship_diff, annot=True, fmt='g', cmap='coolwarm',center=0)
    #plt.title('Relationship between genres')
    plt.xlabel('', fontsize=20)
    plt.ylabel('', fontsize=20)
    ax.xaxis.tick_top()
    plt.xticks(rotation=30, ha='left')
    plt.yticks(rotation=0)
    for i in range(len(relationship_diff)):
        for j in range(len(relationship_diff.columns)):
            if not np.isnan(relationship_diff.iloc[i,j]):
                if abs(t_value_matrix.iloc[i,j]) > t_crit[2]:
                    ax.text(j+0.5, i+0.85, '***', ha='center', va='center', color='black', fontsize=20)
                elif abs(t_value_matrix.iloc[i,j]) > t_crit[1]:
                    ax.text(j+0.5, i+0.85, '**', ha='center', va='center', color='black', fontsize=20)
                elif abs(t_value_matrix.iloc[i,j]) > t_crit[0]:
                    ax.text(j+0.5, i+0.85, '*', ha='center', va='center', color='black', fontsize=20)
    if save:
        plt.savefig('./plot/relationship_filtered_%s.png'%figure_name, dpi=300, bbox_inches='tight', transparent=True)
    plt.show()