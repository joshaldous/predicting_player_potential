import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import datetime as dt
from bs4 import BeautifulSoup as BS
import functools
import time
import requests
import csv
import re

df = pd.read_csv('../data/scrp_data/all_play_stats.csv')  #import scraped data

df.year = df.year.str.replace("'",'').str.replace('[','').str.replace(']','')

df.columns = ['years_played','age_at_season','squad','country','competition','lg_rank','mat_played','starts','minutes','goals','assists',
              'penalties','pk_att','yellow_cards','red_cards','goals_p90','assists_p90','g+a_p90','g-pk_p90','g+a-pk_p90','matches',
              'player_name','position','year_of_season']

df = df.loc[df.count(1) > df.shape[1]/2, df.count(0) > df.shape[0]/2]  # removes all rows that are more than half nan

df['year'] = df['year_of_season'].apply(lambda x: x[:4]) # converts a column of year of season information ('2017-2018') to an int of the year the season started
df.year = df.year.astype(int)
df.sort_values(by=['player_name'])
df.drop(['matches'],axis=1,inplace=True)

conn = sqlite3.connect('/home/josh/Documents/dsi/caps/cap2/predicting_player_potential/data/database.sqlite')   # connect to kaggle data
c = conn.cursor()

tab1 = '''select * from Player'''
c.execute(tab1)

play_data = c.fetchall()
df_player = pd.read_sql('select * from Player',con=conn) # import the Player table
df_play = df_player.copy()
df_play.drop(['id','player_api_id'],axis=1,inplace=True)
df_play.birthday = pd.to_datetime(df_play.birthday,format='%Y/%m/%d')   # create an age now column by subtracting today's date and date born (to be used for finding retired players) 
df_play['age_now'] = [abs(x - pd.to_datetime(dt.date.today())) for x in df_play.birthday]
df_play.age_now = df_play.age_now/dt.timedelta(days=365)

df_player_atts = pd.read_sql('select * from Player_Attributes',con=conn)  # import the Player_Attributes table from the kaggle dataset
df_atts = df_player_atts.copy()
df_atts.date = pd.to_datetime(df_atts.date,format='%Y/%m/%d')
df_atts.drop(['id','player_api_id'],axis=1,inplace=True)

df1 = pd.merge(df_play,df_atts,how='left',on='player_fifa_api_id')  # merge the Player and Player_Attributes table
df1 = df1.loc[df1.count(1) > df1.shape[1]/2, df1.count(0) > df1.shape[0]/2]
df1['year'] = pd.DatetimeIndex(df1['date']).year
df1['age_at_season'] = df1.date - df1.birthday
df1.age_at_season = df1.age_at_season/dt.timedelta(days=365)

df_tot = pd.merge(df,df1,how='outer',on=['player_name','year']) # merge the kaggle dataframe and scraped dataframe

df = df_tot.drop(['age_at_season_y','date','year','player_fifa_api_id','birthday'],axis=1) 
df.columns = ['years_played','age_at_season','squad','country','competition','lg_rank','mat_played','starts',
              'minutes','goals','assists', 'pens_scored','pens_att','yell_cards','red_cards','goals_p90',
              'assts_p90','g+a_p90','g-pens_p90','g+a-pens_p90','player_name','position','year_of_season',
              'height','weight','age_now','overall_rating','potential','foot','attack_rate','defense_rate',
              'crossing','finishing','head_acc','short_pass','volleys','dribble','curve','freekick_acc',
              'long_pass','ball_control','acceleration','sprint_speed','agility','reactions','balance','shot_power',
              'jumping','stamina','strength','long_shot','aggression','interceptions','positioning','vision',
              'pen_rating','marking','stand_tackle','slide_tackle','gk_dive','gk_hands','gk_kick','gk_position',
              'gk_reflex']

df.position = df.position.str.encode('ascii','ignore').str.decode('ascii')  # there were some non-ascii characters in some of the position field scraped data. this removes them
df_position = df[df.position.notna()] # drops all position rows with nan positions

df_position = df_position[df_position.minutes.notna()]   # cleaning data and dropping nans
df_position.minutes = df_position.minutes.str.replace(',','')
df_position.minutes = df_position.minutes.astype(int)
df_position = df_position[df_position.foot.notna()]
df_position.foot = df_position.foot.str.replace('right','0')
df_position.foot = df_position.foot.str.replace('left','1')
df_position.foot = df_position.foot.astype(int)
df_position.attack_rate = df_position[['attack_rate']].fillna('1')
att_repl = {'high':'4','medium':'3','low':'1','norm':'3','le':'1','None':'1','stoc':'1','y':'1'}
for k, v in att_repl.items():
    df_position.attack_rate = df_position.attack_rate.str.replace(k,v)
df_position.attack_rate = df_position.attack_rate.astype(int)
df_position.defense_rate = df_position[['defense_rate']].fillna('1')
def_repl = {'high':'4','medium':'3','low':'1','ormal':'3','o':'1','ean':'3','_0':'1','t1cky':'1','es':'1'}
for k, v in def_repl.items():
    df_position.defense_rate = df_position.defense_rate.str.replace(k,v)
df_position.defense_rate = df_position.defense_rate.astype(int)

class PositionDF(pd.DataFrame):         # create a class for splitting the total df into player position dfs
    @property
    def _constructor(self):
        return PositionDF     

    def create_position_df(self,position):
        return self[self.position.str.contains(position)]

    def create_overage_df(self,age):
        return self[self.age_now >= age]
    
    def create_underage_df(self,age):
        return self[self.age_now < age]

    def add_targets(self,list_of_targets):
        self['target'] = np.where(self['player_name'].isin(list_of_targets),1,0)
        return self

    def yes_no_split(self,yes_no_split=True):
        dfy = self[self.target == 1]
        dfn = self[self.target == 0]
        return dfy, dfn
    
df_all_positions = PositionDF(df_position)  # create a database for all positions from the class

fw32_targ_lst = ['Urby Emanuelson','Samuel Eto\'o','Jason Euell','Ewerthon','Santiago Ezquerro','Steven Fletcher','Mikael Forssell',        # targets = 1 for fw 32 y.o. and older. this 
                 'Robbie Fowler','Pierre-Alain Frau','Fred','Alexander Frei','Ricardo Fuller','Gabri','Theofanis Gekas','Ryan Giggs',       # was done by hand in this instance. i spent
                 'Alberto Gilardino','Ludovic Giuly','Grafite','Asamoah Gyan','Hamdi Harbaoui','Vahid Hashemian','Patrick Helmes',          # way too long trying to find other ways to 
                 'Henrique','Thierry Henry','Emile Heskey','Grant Holt','Hulk','Vincenzo Iaquinta','Filippo Inzaghi','Jefferson Farfan',    # do this. something to consider in capstone3
                 'Andrew Johnson','Jonas','Kenwyne Jones','Nihat Kahveci','Bonaventure Kalou','Nwankwo Kanu','Robbie Keane','Kiko',
                 'Diego Klimowicz','Miroslav Klose','Danny Koevermans','Dirk Kuyt','Rickie Lambert','Ezequiel Lavezzi','Nikos Liberopoulos',
                 'Lima','Joseba Llorente','Cristiano Lucarelli','Roy Makaay','Florent Malouda','Mancini','Marcelinho','Fabrizio Miccoli',
                 'Michu','Miku','Diego Milito','Bruno Moreira','Daniel Moriera','Fernando Morientes','Adrian Mutu','Oliver Neuville',
                 'Mamadou Niang','Nilmar','Ruud van Nistelrooy','Ricardo Oliveira','Michael Owen','Walter Pandiani','Roman Pavlyuchenko',
                 'Robin van Persie','Kevin Phillips','Lukas Podolski','Rivaldo','Robinho','Tomasso Rocchi','Hugo Rodallega','Ronaldinho',
                 'Bryan Ruiz','Andriy Shevchenko','Jonathan Soriano','Moussa Sow','David Suazo','Humberto Suazo','Francesco Tavano','Luca Toni',
                 'Francesco Totti','David Trezeguet','Arda Turan','Marama Vahirua','Mathieu Valbuena','Darius Vassell','Mark Viduka',
                 'Christian Vieri','Willian','Sylvain Wiltord']

if __name__ == '__main__':
    df_fw = df_all_positions.create_position_df('FW')    # create a forward specific postion dataframe
    df_fw.drop(['gk_reflex','gk_dive','gk_hands','gk_kick','gk_position','yell_cards','red_cards'],axis=1,inplace=True) # drop position specific columns
    df_fw32 = df_fw.create_overage_df(32)
    df_fw_playing = df_fw32.create_underage_df(32)
    df_fw32_full = df_fw32.add_targets(fw32_targ_lst)
    df_fw32_yes, df_fw32_no = df_fw32_full.yes_no_split()

    df_cb = df_all_positions.create_position_df('CB')  # create a database for centerbacks from the class
    df_cb.drop(['gk_reflex','gk_dive','gk_hands','gk_kick','gk_position','pens_scored','pens_att','pen_rating'],axis=1,inplace=True)  # drop position specific columns
    df_cb_retd = df_cb.create_overage_df(32)
    df_cb_yng = df_cb.create_underage_df(32)

    df_def = df_all_positions.create_position_df('DEF')  # create a database for all defensive positions
    df_def.drop(['gk_reflex','gk_dive','gk_hands','gk_kick','gk_position'],axis=1,inplace=True)
    df_cb_retd = df_def.create_overage_df(32)
    df_cb_yng = df_def.create_underage_df(32)

    df_mf = df_all_positions.create_position_df('MF') # create a database for all midfield postions
    df_mf.drop(['gk_reflex','gk_dive','gk_hands','gk_kick','gk_position'],axis=1,inplace=True)
    df_mf_retd = df_mf.create_overage_df(32)
    df_mf_yng = df_mf.create_underage_df(32)

    df_gk = df_all_positions.create_position_df('GK')  # create a database for goalkeepers 
    df_gk.drop(['pens_scored','pens_att','goals','assists','goals_p90','assts_p90','g+a_p90','g-pens_p90','g+a-pens_p90',
                'attack_rate','defense_rate','crossing','finishing','head_acc','volleys','dribble','curve','freekick_acc',
                'acceleration','sprint_speed','shot_power','long_shot','interceptions','pen_rating','marking'],axis=1,inplace=True)
    df_gk_retd = df_gk.create_overage_df(32)
    df_gk_yng = df_cb.create_underage_df(32)
    
    df_tot.to_csv('../data/scrp_data/total_df.csv') # push to csv to save and import from another function
    df_fw32_full.to_csv('../data/cln_dfs/fw32.csv') 
    