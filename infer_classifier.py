from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pickle
import torch
torch.cuda.empty_cache()
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# Load the df dataframe
with open('data/df.pickle', 'rb') as f:
    df = pickle.load(f)


# Load the saved model
model = AutoModelForSequenceClassification.from_pretrained("model", num_labels=2)
model.to(device)
model.eval()

# Load the encoder
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")


# Choose the df with type = 'mushroomkingdom'
df_predict = df[df['type'] == 'mushroomkingdom']
# Choose the rows with body not in ['[deleted]', '[removed]'] and not empty
df_predict = df_predict[~df_predict['body'].isna()]
df_predict = df_predict[~df_predict['body'].isin(['[deleted]', '[removed]'])]



text = df_predict['body'].tolist()
predictions = []
for index, body in enumerate(text):
    try:
        encoded = tokenizer(body, padding=True, truncation=True, return_tensors="pt").to(device)
        # Get the predictions
        prediction = model(**encoded)
        prediction = prediction.logits.argmax(dim=-1).tolist()
    except:
        prediction = 0.5
    predictions.append(prediction[0])
    print(index)

df_predict['pred'] = predictions


pattern = r"/r/(\w+)/"
# Get the subreddit from the body
df_predict['subreddit'] = df_predict['body'].str.extract(pattern, expand=False)
# lower the subreddit
df_predict['subreddit'] = df_predict['subreddit'].str.lower()
# Get unique subreddits
subreddits = df_predict['subreddit'].unique()
# Get the number of unique subreddits
len(subreddits)
# List the subreddit and the number of posts
df_predict['subreddit'].value_counts()
#
df_predict_nan = df_predict[df_predict['subreddit'].isna()]
# Replace nan with 'gameswap'
df_predict['subreddit'] = df_predict['subreddit'].fillna('gameswap')
# Save the df_predict dataframe by pickle
with open('data/df_predict.pickle', 'wb') as f:
    pickle.dump(df_predict, f)

# Combine df_predict and df by index
for index, row in df_predict.iterrows():
    df.loc[index, 'pred'] = row['pred']
    df.loc[index, 'subreddit'] = row['subreddit']

# Save the df dataframe by pickle
with open('data/df_combine_predict.pickle', 'wb') as f:
    pickle.dump(df, f)


# Replace nan in subreddit by type
df['subreddit'] = df['subreddit'].fillna(df['type'])

import matplotlib.pyplot as plt
plt.clf()
df[df['subreddit'] == 'gameswap'].groupby('created_utc').count()['index'].cumsum().plot()
df[df['subreddit'] == 'gamesale'].groupby('created_utc').count()['index'].cumsum().plot()
plt.legend(['gameswap', 'gamesale'])
plt.show()