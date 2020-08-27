# Predicting Player Potential

<p align='center'>
  <img src='https://media.giphy.com/media/p3cgmVTX2kcdV3GUUj/giphy.gif' width='450' height='300' />
</p>

## Table of Contents

  1. [Overview](#Overview)
  2. [Question and Hypothesis](#Question-and-Hypothesis)
  3. [Exploratory Data Analysis](#Exploratory-Data-Analysis)
  4. [Visualization](#Visualization)
  5. [Conclusion](#Conclusion)
  6. [Credits](#Credits)
  7. [Future Actions](#Future)

<a name="#overview"></a>
## Overview - Can we predict if a young player will be worthy of a transfer investment using retired player stats?

In the world of professional football, finding the right players for the right money is vitally important to every team. Instead of drafting and trading players, footballers are bought and sold by their teams. And with the large injection of TV money, footballer transfer value inflation has gone through the roof. A team that wants to obtain a player under contract from another team has to agree a price with the other team to purchase the player and agree an annual salary and contract length with the player.  For example, Arsenal's transfer record is 72,000,000 pounds paid to Lille for Nicolas Pepe.  Their record contract is 350,000 pounds per week, over 4 years, given to Mesut Ozil.  These massive outlays can make or break teams, so finding the correct player is imperative.  If a team can find a young, inexpensive player that they can develop into a world-class star, they are ahead of the curve. 

I found a Kaggle sqlite database (here) that has 10,000 players and their attributes.  The players table has information for birthday, height, and weight.  The player_attribute table has infomation for EA Sports FIFA ratings.  FIFA is a popular computer and console football game where each player is given a rating for attributes such as shooting, volleying, slide tackling, goalkeeper positioning, sprint speed, acceleration, etc.  This is not ideal however because FIFA attribute ratings are notoriously debatable and reems of paper and countless YouTube and Instragram hours have been used up arguing these numbers. That said, it is about as good of an approximation available without having access to direct team-coaching data. 

The great thing about this Kaggle data is that it has multiple years for the players.  This shows the development of the players (especially older players) along their career arc.  With this in mind, the plan has been to combine the Kaggle data for each player with their annual playing stats. Things like goals, assists, minutes played, yellow cards per year.  This data is very specific and not available in any one dataset so i had to scrape it individually for each player. Luckily, there is a fantastic website for all your sporting needs. sports-reference.com has stats for all major sports including football (FBRef.com), the NFL (Pro-Football-Reference.com) and college sports. FBref.com has year to year stats for nearly 200,000 players ranging from the super-talented and famous to the most obscure.  A good deal of the past week was spent learning how to scrape the table that I wanted from FBref for each player and aggregating it into a single dataframe.  

<a name="#markdown-header-quest&hyp"></a>
## Questions

Given all of the above, the question must be asked.  How can teams get ahead?  Is it possible to find a combination of statistics that would allow a team to get an insight into player potential? If it is possible, what are the metrics by which a team should judge a player?  

My aim with this project is to 

<a name="#markdown-header-EDA"></a>
## Exploratory Data Analysis
I found a great resource on [Kaggle](https://www.kaggle.com/irkaal/english-premier-league-results) from a user named irkaal. This csv contains all the games from the beginning of the 2000-2001 season through to matches played this month. The major concern was that the referee's names were in several different forms. My solution to this was to create a referee dictionary with the last names of the referees as the keys and a string of first and last names as the values.  To do this, I separated the last names in the referee column and created a new column.  Next I created a list of referees based on those names in a text file.  Lastly, I combined the last names and list into a dictionary and created a new 'ref_name' column in my data frame that input the full standardized name of the ref from the dictionary.  {:toc}
Other than that, the data was solid.  There were about 25 rows of Nan values at the end that I lopped off, and I had to change the 'Date' column from a string to a datetime format, but minor switches.  The code I used to clean my data can be found [here](https://github.com/joshaldous/Galvinize-Capstone1/blob/master/src/EDACap1.py).
<a name="#markdown-header-graphs"></a>
## Visualization

As a general formula, home teams tend to attack and be on the front foot more, while away teams try to keep an organized, defensive shape and patiently wait for oppurtunities to score.  At least that is how it was for most of the 20th century.  That formula is shifting to more of one where certain teams play certain ways regardless of where the match is held, but for at least the early part of my data, that could be considered to be a factor.  However, even if this is the case, there is still plenty of time in a match for home team players to be booked.  There are fast-breaking counter-attacks, tired-legs and tired-minds which can lead to rash decisions, and no team controls the ball for 90% of 90 minutes. So, straight away I wanted to see if the number of cards given to home teams was about equal to the number of cards given to away teams as a starting point.  

<p align="center">
  <img width="850" height="425" src="./images/total_card_pie.png">
</p>

So you are more likely to be booked on the road. This got me a bit more interested and so I started to dig into the data more.  What do the scatter plots look like when you plot the home cards against the away cards?  I added in a diagonal line to show where we would expect the numbers to be if the distribution was truly random.

<p align="center">
  <img width="1000" height="450" src="./images/Home_and_Away_Yellows_Brandished_per_Referee_(Season_2000-2020).png">
</p>

<p align="center">
  <img width="1000" height="450" src="./images/Home_and_Away_Reds_Brandished_per_Referee_(Season_2000-2020).png">
</p>

When I first looked at the Red Card scatter plot, I was surprised to see that most of the referees were on the 'home' side of the diagonal line.  The number of away reds are a greater propotion of the total red cards than the away yellows.  How could this be?  After a second glance, I noticed that the y-axis is twice what the x-axis values are.  This makes more sense.  In a one-to-one scatter plot, the dots representing each referee would be higher, but the graph overall would be more stretched out.  

There is one more visualization that I think makes this point clearly. The mean number of games reffed by a Premier League referee is about 120.  That's a little more than 3 seasons of games.  To get this number of games, the Professional Game Match Officials Limited (PGMOL), the group that oversees EPL officials, must hold you in high esteem.  Only 24 referees have done it.  These refs have to be the best at being impartial and calling matches according to the current rules.  The following graphs show the number of home and away cards shown by these top officials.

<p align="center">
  <img width="1000" height="450" src="./images/Home_and_Away_Yellow_Cards_for_Referees_that_have_Overseen_at_least_120_Games.jpeg">
</p>

<p align="center">
  <img width="1000" height="450" src="./images/Home_and_Away_Red_Cards_for_Referees_that_have_Overseen_at_least_120_Games.jpeg">
</p>

With the data prepared, I was ready to run my test.
<a name="#markdown-header-conclusion"></a>
## Conclusion

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

  1. I do not own, nor pretend to own any data, images, or copyrights having to do with the Premier League.  
  2. Data for the analysis was obtained from https://www.kaggle.com/irkaal/english-premier-league-results
  3. All plot were created by me using the data obtained and matplotlib.

<a name="#Future"></a>
## In the Future

If I continue to pursue this project, I hope to accomplish the following:
  1. More precisely reduce the number of features
  2. Expand the predictions to other positions
  3. Use more specific postions
  4. Try other Unsupervised Models as inputs to the supervised final model
  5. Try other Supervised Models as the final model
  6. 


