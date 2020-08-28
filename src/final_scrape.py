import numpy as np
import pandas as pd
import sqlite3
import datetime as dt
from bs4 import BeautifulSoup as BS
import time
import requests
import csv
import re

conn = sqlite3.connect('/home/josh/Documents/dsi/caps/cap2/predicting_player_potential/data/database.sqlite')
c = conn.cursor()
tab1 = '''select * from Player'''
c.execute(tab1)
play_data = c.fetchall()

df_player = pd.read_sql('select * from Player',con=conn)
df_player.head()

player_list = sorted(list(df_player.player_name.unique()))

def name_location_scrapper(url):
    r = requests.get(url)
    soup = BS(r.content,'html.parser')
    bod = soup.find_all('body')
    div_list = bod[0].find_all('div',attrs={'class':'section_content'})
    a_list = div_list[0].find_all('a')
    return ['https://fbref.com'+x['href'] for x in a_list]

def name_scrapper(url_lst):
    href_list = []
    player_scrp_lst = []
    for url in url_lst:
        r = requests.get(url)
        soup = BS(r.content,'html.parser')
        bod = soup.find_all('body')
        div_list = bod[0].find_all('div',attrs={'class':'section_content'})
        a_list = div_list[0].find_all('a')
        for a_ in a_list:
            href_list.append('https://fbref.com' + a_['href'])
            player_scrp_lst.append(a_.text)
        wait = np.random.randint(4,size=1)
        time.sleep(wait)
    return player_scrp_lst, href_list

def save_to_csv(input, output):
    with open(output,'w') as myfile:
        wr = csv.writer(myfile,quoting=csv.QUOTE_ALL)
        wr.writerow(input)

play_nm = pd.read_csv('../data/scrp_data/player_data_name_lst.csv',sep = ',',header=None)
play_webs = pd.read_csv('../data/scrp_data/web_data_loc.csv',sep= ',',header=None)
df_lookup = pd.concat((play_nm.transpose(),play_webs.transpose()),axis=1)
df_lookup.columns = ['p_name','fbref_loc']

play_look_lst = player_list

def player_data_df_creator(dataframe):
    url = dataframe.iloc[0,1]
    r = requests.get(url)
    soup = BS(r.content,'html.parser')
    h1s_ = soup.find_all('h1')
    play_nm = [item.get_text(strip=True) for item in h1s_[0].select("span")][0]
    p_strong = [item.next_sibling for item in soup.select("p strong")][:3]
    p_pos = re.sub(r'\n+.','',p_strong[1])
    tbod = soup.find_all('tbody')
    thead = soup.find_all('thead')
    head_rows = thead[0].find_all('tr')
    for hr in head_rows:
        hds = hr.find_all('th')
        cols = [hd.text for hd in hds[1:]]
    trows = tbod[0].find_all('tr')
    data = []
    y_played = []
    for tr in trows:
        tds = tr.find_all('td')
        yrs = tr.find_all('th',attrs={'scope':'row'})
        yr = [y.text for y in yrs]
        row = [td_.text for td_ in tds]
        data.append(row)
        y_played.append(yr)
    df = pd.DataFrame(data,columns=cols)
    df['player_name'] = [play_nm for _ in range(len(data))]
    df['position'] = [p_pos for _ in range(len(data))]
    df['year'] = y_played
    
    return df
    
def player_data_appender(df_to_append,df_to_search):
    for site in df_to_search.fbref_loc:
        url2 = site
        print(url2)
        r2 = requests.get(url2)
        soup2 = BS(r2.content,'html.parser')
        try:
            h1s2 = soup2.find_all('h1')
            play_nm2 = [item.get_text(strip=True) for item in h1s2[0].select("span")][0]
            p_strong2 = [item.next_sibling for item in soup2.select("p strong")][:3]
            p_pos2 = re.sub(r'\n+.','',p_strong2[1])
            tbod2 = soup2.find_all('tbody')
            thead2 = soup2.find_all('thead')
            head_rows2 = thead2[0].find_all('tr')
            for hr2 in head_rows2:
                hds2 = hr2.find_all('th')
                cols2 = [hd.text for hd in hds2[1:]]
            trows2 = tbod2[0].find_all('tr')
            data2 = []
            y_played2 = []
            for tr2 in trows2:
                tds2 = tr2.find_all('td')
                yrs2 = tr2.find_all('th',attrs={'scope':'row'})
                yr2 = [y2.text for y2 in yrs2]
                row2 = [td2.text for td2 in tds2]
                data2.append(row2)
                y_played2.append(yr2)
            df_new = pd.DataFrame(data2,columns=cols2)
            df_new['player_name'] = [play_nm2 for _ in range(len(data2))]
            df_new['position'] = [p_pos2 for _ in range(len(data2))]
            df_new['year'] = y_played2
            df_to_append = pd.concat([df_to_append,df_new],axis=0,join='outer')
            df_to_append.to_csv('../data/scrp_data/working_player_stats.csv')
        except:
            pass
        wait = np.random.randint(3,size=1)
        time.sleep(wait)
    
    return df_to_append





if __name__ == '__main__':
    name_url_lst = name_location_scrapper('https://fbref.com/en/players/')
    
    player_web_lst, href_lst = name_scrapper(name_url_lst)
    
    save_to_csv(player_web_lst,'../data/scrp_data/player_data_name_lst.csv')
    save_to_csv(href_lst,'../data/scrp_data/web_data_loc.csv')

    final_play_df = df_lookup[df_lookup['p_name'].isin(play_look_lst)]
    final_play_csv = final_play_df.to_csv('../data/scrp_data/final_player_csv.csv')
    df = player_data_df_creator(final_play_df)

    player_stats = player_data_appender(df_to_append=df,df_to_search=final_play_df)
    all_play_stats = player_stats.to_csv('../data/scrp_data/all_play_stats.csv')