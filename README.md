# Predicting Player Potential

<p align='center'>
  <img src='https://media.giphy.com/media/p3cgmVTX2kcdV3GUUj/giphy.gif' width='450' height='300' />
</p>

## Table of Contents

  1. [Overview](#Overview)
  2. [Questions and Goals](#Question-and-Goals)
  3. [Exploratory Data Analysis](#Exploratory-Data-Analysis)
  4. [Visualization](#Visualization)
  5. [Conclusion](#Conclusion)
  6. [Credits](#Credits)
  7. [Future Actions](#Future)

<a name="#overview"></a>
## Overview - Can we predict if a young player will be worthy of a transfer investment using retired player stats?

In the world of professional football, finding the right players for the right money is vitally important to every team. Instead of drafting and trading players, footballers are bought and sold by their teams. And with the large injection of TV money, footballer transfer value inflation has gone through the roof. A team that wants to obtain a player under contract from another team has to agree a price with the other team to purchase the player and agree an annual salary and contract length with the player.  For example, Arsenal's transfer record is 72,000,000 pounds paid to Lille for Nicolas Pepe.  Their record contract is 350,000 pounds per week, over 4 years, given to Mesut Ozil.  These massive outlays can make or break teams, so finding the correct player is imperative.  If a team can find a young, inexpensive player that they can develop into a world-class star, they are ahead of the curve. 

I found a Kaggle sqlite database (https://www.kaggle.com/hugomathien/soccer/data) that has 10,000 players and their attributes. However, the majority of the tables are related to historical gambling predictions. The keys to the columns in other tables is included in the [cap2_notes.txt](https://github.com/joshaldous/predicting_player_potential/cap2_notes.txt) file. The players table has information for birthday, height, and weight.  The player_attribute table has infomation for EA Sports FIFA ratings.  FIFA is a popular computer and console football game where each player is given a rating for attributes such as shooting, volleying, slide tackling, goalkeeper positioning, sprint speed, acceleration, etc.  This is not ideal however because FIFA attribute ratings are notoriously debatable and reems of paper and countless YouTube and Instragram hours have been used up arguing these numbers. That said, it is about as good of an approximation available without having access to direct team-coaching data. 

The great thing about this Kaggle data is that it has multiple years for the players.  This shows the development of the players (especially older players) along their career arc.  With this in mind, the plan has been to combine the Kaggle data for each player with their annual playing stats. Things like goals, assists, minutes played, yellow cards per year.  This data is very specific and not available in any one dataset so i had to scrape it individually for each player. Luckily, there is a fantastic website for all your sporting needs. [Sports-Reference.com](https://www.sports-reference.com) has stats for all major sports including football [FBRef.com](https://www.fbref.com), the [NFL](https://www.Pro-Football-Reference.com) and [College Basketball](https://www.sports-reference.com/cbb/). <!---->FBref.<!---->com has year to year stats for nearly 200,000 footballers ranging from the super-talented and famous to the most obscure.  A good deal of the past week was spent learning how to scrape the table that I wanted from FBref for each player and aggregating it into a single dataframe.  

<a name="#markdown-header-quest&hyp"></a>
## Questions and Goals

Given all of the above, the question must be asked.  How can teams get ahead?  Is it possible to find a combination of statistics that would allow a team to get an insight into player potential? If it is possible, what are the metrics by which a team should judge a player?  

The immediate and most basic goal is to see if a model can be built to predict if a player is worthy of a transfer investment for a certain position. Beyond that, it would be ideal to create a model could take any position into account, possibly even predict the best positions for players that don't have an obvious position. 

Originally, trying to create a model to predict player potential (a FIFA attribute in the kaggle dataset) was considered, but this was deemed to reliant on the FIFA attributes given and the FIFA methodology. So I opted for a Invest/Don't Invest (simple binary target) for the position databases that I created.  I am aware that this decision also comes with its own drawbacks and questions, but it seemed the best route for the time allotment. However, because of that time constraint, I only got through one position, forwards.

<a name="#markdown-header-EDA"></a>
## Exploratory Data Analysis  
I found a great resource on [Kaggle](https://www.kaggle.com/hugomathien/soccer/data) from a user named hugomathien. This sqlite database contains over 10,000 player stats and attributes that allowed me to find out players current age.  It also contained the FIFA ratings for 40 footballing attributes. Since the kaggle database allowed me to see the attributes over several years of a players career, I wanted to match up the actual statistics for each player for that given year.  Stats like goals, goals per 90 minutes, minutes played, and so forth. I looked all over the internet for a dataset that might provide me with this information, but it came down to football reference and scraping the data.

In order to get the names that I needed, I made a list of all the names in kaggle database, and scraped the fbreference player search pages to find the location of that player's stat page. With all the pages needed, it was a matter of scraping the correct table from each player. This is not as straightforward as it might sound, because not all the tables with the information I was looking for are the same size, and scraping 10,000 pages takes a bit of time. In the end, my lack of experience in scraping caused me to lose quite a few players from the list. This is unfortunate, and given more time, I feel I would have rectified the issue and pull all the data I was trying to obtain. The code I used to scrape the data can be found [here](https://github.com/joshaldous/predicting_player_potential/tree/master/src/final_scrape.py). 


From there, the data-cleaning was not too complicated. It was cleaning strings, formatting dates and figuring out what to do with nans. Different nans are different beasts, and so have to be dealt with in specific ways. Once the data was clean, I ran into a major issue. I could not figure out how to create the targets I was looking for. I spent a lot of time trying to figure out a way to get the code to figure it out automatically, but I couldn't get it right.  This is I could look at in the future, but it may not be possible.  There are so many variables and the target is very specific. 

In the end I had to manually create a list of the 'quality' forwards that had very good careers. I did this by going through the names, verifying their career stats and voting yes/no on individual players. This would not be tenable for further positions or larger datasets. The code I used to clean my data can be found [here](https://github.com/joshaldous/predicting_player_potential/tree/master/src/final_eda.py).
<a name="#markdown-header-graphs"></a>
## Visualization

The initial data kaggle data looks like the following:

<p align="center">
  <img width="1250" height="525" src="./images/df_ahead.png">
</p>

I dumped the scraped data into a csv and it turned out pretty well, except for the missing players. After the EDA and merging the dataframes on player names and individual years, I went about creating a model.    

So you are more likely to be booked on the road. This got me a bit more interested and so I started to dig into the data more.  What do the scatter plots look like when you plot the home cards against the away cards?  I added in a diagonal line to show where we would expect the numbers to be if the distribution was truly random.

<p align="center">
  <img width="1000" height="450" src="./images/Home_and_Away_Yellows_Brandished_per_Referee_(Season_2000-2020).png">
</p>

<p align="center">
  <img width="1000" height="450" src="./images/Home_and_Away_Reds_Brandished_per_Referee_(Season_2000-2020).png">
</p>

When I first looked at the Red Card scatter plot, I was surprised to see that most of the referees were on the 'home' side of the diagonal line.  The number of away reds are a greater propotion of the total red cards than the away yellows.  How could this be?  After a second glance, I noticed that the y-axis is twice what the x-axis values are.  This makes more sense.  In a one-to-one scatter plot, the dots representing each referee would be higher, but the graph overall would be more stretched out.  

There is one more visualization that I think makes this point clearly. The mean number of games reffed by a Premier League referee is about 120.  That's a little more than 3 seasons of games.  To get this number of games, the Professional Game Match Officials Limited (PGMOL), the group that oversees EPL officials, must hold you in high esteem.  Only 24 referees have done it.  These refs have to be the best at being impartial and calling matches according to the current rules.  The following graphs show the number of home and away cards shown by these top officials.irkaal/english-premier-league-results
In order to see if the difference card count was significant, I decided to run a z-test.  I could calculate the sample mean and standard deviation and had a sufficient number of samples, so I imported weightstats from statsmodels.stats for a 2-variable z-test. I ran the yellow cards first.  hnorm_yell.pdf(x) is the normal distribution for home yellow cards over the interval [-2,5], and anrom_yell.pdf(x) is the normal distribution for away yellows over that same interval. Degrees of freedom is one minus the number of matches in the sample, since each match is independent and random.  The p-value for this test was 0.997, which is much greater than my alpha of 0.25.  
    
    statmodel.ztest(hnorm_yell.pdf(x),anorm_yell.pdf(x),ddof=7569)
    (0.0033134485216764734, 0.9973562554191262)

Next, to the red cards. hnorm_red.pdf(x) is the normal distribution for home red cards over the interval [-1,1.5], with anorm_red.pdf(x) the normal distribution for away red cards over that same interval. The p-value for this test was 0.999, also much greater than my alpha of 0.25.
{:toc}
    statmodel.ztest(hnorm_red.pdf(x),anorm_red.pdf(x),ddof=7569)
    (4.0847710039192654e-11, 0.9999999999674083)

In both cases, I cannot reject the null hypothesis.  In fact, the referees should be commended for their impartiatility.  I have two more visualizations to reinforce the result of the z-test.

<p align="center">
  <img width="800" height="400" src="./images/Home_yellow_normdist.jpeg">
</p>

<p align="center">
  <img width="800" height="400" src="./images/Home_red_normdist.jpeg">
</p>

<a name="#markdown-header-Credits"></a>
## Credits

  1. I do not own, nor pretend to own any data or images in the above presentation.  
  2. Data for the analysis was obtained from https://www.kaggle.com/hugomathien/soccer/data and https://fbref.com

<a name="#Future"></a>
## In the Future

If I continue to pursue this project, I hope to accomplish the following:
  1. Find a way to automate target allocation
  2. More precisely reduce the number of features
  3. Use more specific postions
  4. Try other Unsupervised Models as inputs to the supervised final model
  5. Try other Supervised Models as the final model
  6. Expand the predictions to other positions


