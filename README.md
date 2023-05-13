# An Analysis on Game Exchange and Game Sales Platforms

## Data
Run 00_data_preprocessing.ipynb to get the data ready for analysis. The data is stored in the data folder. 

### History of members
- gamesale_member.pickle gameswap_member.pickle are the data of history members for game sales and game exchange platforms respectively. 

### IGDB information
- games.pkl stores all the games information on IGDB.
- platforms.pkl
- version.pkl
- console_released_date.pkl stores the released date of each console.
- genres_igdb.pkl stores the genres name and id on IGDB. This is important for the analysis.

### Posts on Reddit
- history.pkl is json data from [SwapNSalebot](https://raw.githubusercontent.com/RegExrTech/SwapBot/master/database/gamesale-swaps.json).
- transformed_history.pkl is transformed from history.pkl, which extracts the **links** to the confirmation posts.
- transformed_data.pkl contains the **text** of the confirmation posts. It's scraped from Reddit.
- df_transformed_data.pkl is the dataframe of transformed_data.pkl, which facilitates the analysis.
- train_data.pkl is the training data for the classification model. It's derived from df_transformed_data.pkl. It contains the **text** and **label** of the confirmation posts. The label is 1 if the post is a r/GameSale post, and 0 for r/GameSwap.

### Match Rappatz et al. (2017) dataset
- games_tbp.csv is the dataset from Rappatz et al. (2017) joined by IGDB information. It stores all the information of games that are listed on r/GameSwap.
- base_similarity.pkl is the similarity matrix of the games on r/GameSwap w.r.t. the IGDB games. It's used to match the games on r/GameSale to the IGDB games.
  - The matching is done by finding the game name on IGDB that has the highest similarity score to the game name on r/GameSwap. The similarity score is calculated by the **fuzz.ratio** function in the **fuzzywuzzy** package. 

### Confirmed transactions number
- df_predict.pkl is the dataframe of the prediction results from 02_Classifier_infer.ipynb, which uses the model trained in 02_Classifier_train.ipynb.
- df_confirmed_prediction.pkl is the dataframe of df_transformed_data.pkl joined by df_predict.pkl. 
  - mushroomkingdom_history.pkl
  - gamesale_history.pkl
  - gameswap_history.pkl
  - The above three dataset are the subset of df_confirmed_prediction.pkl, which only contains the confirmed transactions from the corresponding platform.

### Orignal post
- original_post.pkl contains all the original post information from the confirmation posts. It's scraped from Reddit.
- "df_pre_%s_original.pkl" % time is the dataframe that contains original post created_utc. It's used to calculate the time difference between the original post and the confirmation post.

### Rappatz el al. (20117) dataset
- have.csv
- pairs.csv
- pairs_dense.cvs (contains time)
- wish.csv
- wish_dense.csv (no time)

## Analysis