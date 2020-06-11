#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 13:33:55 2020
@author: MaciejMiernicki
"""
from pyvirtualdisplay import Display
import psycopg2
import pandas as pd

from datetime import datetime
from time import sleep
from timeit import default_timer as timer

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Links and games that I'll be collecting data from
data_source = {'League of Legends':'https://www.twitch.tv/directory/game/League%20of%20Legends?sort=VIEWER_COUNT',
         'Fortnite':'https://www.twitch.tv/directory/game/Fortnite?sort=VIEWER_COUNT',
         'Counter-Strike: Global Offensive':'https://www.twitch.tv/directory/game/Counter-Strike%3A%20Global%20Offensive?sort=VIEWER_COUNT',
         'Minecraft':'https://www.twitch.tv/directory/game/Minecraft?sort=VIEWER_COUNT',
         'Grand Theft Auto V':'https://www.twitch.tv/directory/game/Grand%20Theft%20Auto%20V?sort=VIEWER_COUNT'}

games_ids = {'League of Legends':1,
         'Fortnite':2,
         'Counter-Strike: Global Offensive':3,
         'Minecraft':4,
         'Grand Theft Auto V':5}

#Essential information like end of collection time and time interval between data collections
set_date = datetime(2020,5,15,13,45)
collection_time = datetime(1,1,1)
interval = 60*30

#Loading list of valid languages and converting it to my needs
langs = pd.read_csv('/home/scripter/languages.txt', sep = '|', names = ['alpha_3', 'alpha_3-t', 'alpha_2', 'eng', 'fra'])['eng'].unique()
langs = list(langs)

for i in langs:
    sep_num = i.count(';')
    if sep_num > 0:
        temp = i.split(';')
        for j in temp:
            langs.append(j.replace(' ',''))
        langs.remove(i)
        
#This will be needed later to handle some errors
is_hosting_xpath = "//div[@class='tw-align-middle tw-font-size-7 tw-inline-block tw-mg-b-05 tw-mg-r-05']|//div[@data-a-target='hosting-ui-header']"

#Initiating virtual display
display = Display(visible = 0, size = (800,600))
display.start()

#Setting chromedriver options
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--disable-setuid-sandbox')
options.add_argument('--blink-settings=imagesEnabled=false')
options.headless = True

#Main while loop that goes until set_date
while set_date > collection_time :
    
    start = timer()

    conn = psycopg2.connect(host = '127.0.0.1', port = '5432', database = 'Scraping', user = 'postgres', password = 'Kozakhaslo3214')
    cur = conn.cursor()
    
    #To check if a streamer is already in streamers table to generate a proper id
    cur.execute("""SELECT twitch_name,id FROM streamers""")
    known_streamers = cur.fetchall()
    
    #Initiating chromedriver
    driver = webdriver.Chrome("/usr/bin/chromedriver", options = options)
    
    #Enumerating over games with links 
    for game, link in data_source.items():
        
        #Setting the collection time now so it's easier to group later
        driver.get(link)
        
        #Waiting for the important elements to load in full
        element = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, 
            "//div[@data-target='directory-first-item']"))
        )
        
        source = driver.page_source
        
        #Making soup
        soup = BeautifulSoup(source, features = 'lxml')
        
        #This is the div that contains all the streams
        all_streams = soup.find('div', attrs = {'class':'tw-flex-wrap tw-tower tw-tower--300 tw-tower--gutter-xs'})
        all_streams = all_streams.find_all(lambda x: True if x.has_attr('data-target') else False)
        
        collection_time = datetime.now()
        
        #Getting the data for top 10 streamers in given game
        for i in range(0,10):
            
            #This is done to get a proper streamer_id later on
            is_known = False
            if len(known_streamers) > 0:
                streamer_id = known_streamers[-1][1] + 1
            else:
                streamer_id = 101
            
            curr_stream = all_streams[i]
            
            #This is BeautifulSoup syntax that was the shortest/fastest
            stream_title = curr_stream.h3.text
            streamer_name = curr_stream.p.text
            stream_language = curr_stream.button.text.capitalize()
            viewers = ''
            game_id = games_ids[game]
            channel_link = 'https://www.twitch.tv' + curr_stream.a['href']
            
            #Making sure that the first tag was the language
            if stream_language not in langs:
                
                try:
                    driver.get(channel_link)
                except:
                    print('Problem getting link: ' + channel_link)
                    continue  
                
                #Waiting for the important elements to load
                try:
                    element = WebDriverWait(driver, 25, 0.1).until(
                        EC.visibility_of_element_located((By.XPATH,is_hosting_xpath))
                    )
                except:
                    print('Problem getting link: ' + channel_link)
                    continue
                
                temp_source = driver.page_source
                temp_soup = BeautifulSoup(temp_source, features = 'html5lib')
                
                try:
                    g = temp_soup.find('div', attrs = {'class':'tw-flex tw-flex-column tw-full-width'})
                    f = g.find_all('div', attrs = {'class':'tw-align-middle tw-font-size-7 tw-inline-block tw-mg-b-05 tw-mg-r-05'})
                    viewers = g.find('div', attrs = {'data-a-target':'channel-viewers-count'}).text
                    viewers = viewers.split(' ')[0]
                    viewers = int(viewers.replace(',',''))

                    for i in f:
                        if i.text in langs:
                            stream_language = i.text
                            break
                except:
                    print('Skipping invalid link: ' + channel_link)
                    continue

            else:
                
                try:
                    driver.get(channel_link)
                except:
                    print('Problem getting link: ' + channel_link)
                    continue 
                
                #Waiting for the important elements to load
                try:
                    element = WebDriverWait(driver, 25, 0.1).until(
                        EC.visibility_of_element_located((By.XPATH,is_hosting_xpath))
                    )
                except:
                    print('Problem getting link: ' + channel_link)
                    continue

                temp_source = driver.page_source
                temp_soup = BeautifulSoup(temp_source, features = 'html5lib')
                
                try:
                    viewers = temp_soup.find('div', attrs = {'data-a-target':'channel-viewers-count'}).text
                    viewers = viewers.split(' ')[0]
                    viewers = int(viewers.replace(',',''))
                except:
                    print('Skipping invalid link: ' + channel_link)
                    continue

            for known_streamer in known_streamers:
                if streamer_name == known_streamer[0]:
                    is_known = True
                    streamer_id = known_streamer[1]
             
            if is_known:
                pass
            else:
                known_streamers.append((streamer_name, streamer_id))
                cur.execute("""INSERT INTO streamers VALUES (%s, %s, %s, %s)""", [streamer_id, streamer_name, stream_language, channel_link])

            cur.execute("""INSERT INTO 
                        stream_data (recorded_at,viewers,streamer_id,game_id,stream_language,stream_title)
                        VALUES (%s,%s,%s,%s,%s,%s)""", 
                        [collection_time.isoformat(timespec = 'seconds'), viewers, streamer_id, game_id, stream_language, stream_title])

        
    conn.commit()
    cur.close()
    conn.close()
    driver.close()
    end = timer()
    print('Time in seconds = ' + str(end - start))
    sleep(max([interval - int(end-start),0]))
    
