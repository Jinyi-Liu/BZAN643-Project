# Research Questions
# ===============
#

1. Efficiency between the two platforms: r/GameSwap and r/GameSale. Is exchanging games more efficient?
2. Since we have Oct 2013-Sep 2015 game exchange data, what are the patterns of the game exchange? 
   Do people want to exchange the same type of game or want to try something different?
3. When it comes to game exchange, do people prefer to exchange the game with someone who has 
   exchanged before or someone who has not exchanged before? What's the difference between game sales and game exchange?



# Data
# ====
- We have Oct 2013-Sep 2015 r/GameSwap confirmed transactions data and wish/have list data from other papers.
- From IGDB(https://www.igdb.com/), we have detailed information about all the console games.
- r/GameSale and r/GameSwap have a common bot that stores all the confirmed transaction data. 
  We can get the data from the bot and use it for our analysis.
  - Since the bot changes how to moderate the transactions since 2019 (it doesn't store the direct link to the transaction anymore),
    for simplicity, we choose to use the data from 2013-2018-12-31.
- From Wayback Machine, we can get the history of the number of subscribers of r/GameSale and r/GameSwap.

# 3. Analysis
### 3.1 Efficiency
See 03_Efficiency.ipynb.

### 3.2 Game Exchange Patterns
See 03_Exchanging_Patterns.ipynb.

### 3.3 Reciprocal Relationship between Bartering and Selling
See 03_Reciprocal_Analysis.ipynb.


# Future Work
# ==========
- Maybe using LLM we can get more exchange data from the transaction confirmation post.
- It will lead to a more comprehensive data set and more accurate analysis.
- Current data only has 2013-2015 data. Maybe we can get more data to 2018-12-31 using LLM.