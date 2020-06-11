# Twitch.tv scraping project

In this project I'm scraping data from Twitch.tv and analysing the data. 


# Methodology

I'm scraping data from 5 games on twitch.tv. Those games are:
- League of Legends
- Counter Strike: Global Offensive
- Minecraft
- Grand Theft Auto V
- Fortnite

I'm using the page that has streams sorted by viewer counts to simplify my life a little. I'm collecting data from the first 10 streams on that page. I've been collecting the data every half hour.


I've set up a virtual machine with LAPP to both serve as a database server and the server to run my scraping script. The script runs until set date and I have a CRON to check periodically if the script didn't crash.



## Technologies

I've used Python3 to write the script. I've used the following libraries:
- **PyVirtualDisplay** - so chrome runs correctly on my Ubuntu machine
- **psycopg2** - to connect with the PostgreSQL database
- **datetime, time** - to keep track of time and measure runtime
- **BeautifulSoup** - to extract information from the HTML  of the site
- **pandas, matplotlib, numpy** - to analyse the data
- **Selenium** - to scrape the site

I also used LAPP on Ubuntu 18.04 on my virtual server and pgadmin4 to manage the database more easily.



## Files in this repository

- **linux_script.py** - this is the script I've used for scraping on the virtual machine
- **data_analisys.ipynb** - this is the notebook with some data analysis
- **ERD.pdf** - the ERD for the database
- **db_access.txt** - here are the credentials to access the database if anybody wants to check the data, 10 concurrent connections limit and read-only privileges

## The technical challenges

I've encountered a lot of challenges and also learned a lot during this project. The first thing I had to do was install LAPP on my virtual machine. I didn't know anything about server administration or linux in general but i pulled through with newfound knowledge about **permissions, user management, CRON jobs, package management** etc.

The second problem was that I knew nothing about web scraping in general. I had to learn to use Selenium and BeautifulSoup. Even with tutorials I had some issues because I was running a CLI Ubuntu and I didn't know about headless mode or virtual displays.

I will talk about the countless reasons that made my script stop running. But I wasted 2-3 weeks worth of collecting data just fixing the script. With the way it works, I just set an end-date and until that date the script keeps running. In hindsight, that is a bad solution. What I should've done from the beginning was to change the script to run one time and then set up a CRON job that would run it every 30min. That would mean that if the script crashes I just lose one datapoint and the script starts again 30m later.

In the end I could've had around 2x more data than I have If I just went with the approach above. Well, now I know and I'll use this knowledge in my next project :)


## Problems with the site content itself

When I overcame the technical issues, I encountered problems with the content itself. When I was testing my script on Chrome in MacOS the viewers count was on the page that had all the streams. In that case I only had to visit 5 sites (with some exceptions that I'll get to later) every 30 minutes which meant that my script took roughly 15-30 seconds to run every time. On Ubuntu however, on a virtual display in headless Chrome, the viewer count on the same page was rounded which meant that my data would be inaccurate. 

If a streamer had 16245 viewers, the HTML code would say he/she had 16,2k viewers, so I would be wrong by anywhere from 1-99 people. I decided to change my script so it would enter the URL for each stream separately instead of scraping the data from the list of top streamers. That way my numbers would be accurate but the runtime of the entire script jumped to ~150s. The increase wasn't 10x because the majority of time in the previous script was taken by initialising chromedriver and writing data to my PostgreSQL database. 

The next issue was with determining the language spoken on stream. Fortunately twitch has a tag system that always includes the language. Unfortunately it isn't always the first tag so I had to find a list of every language in the world, convert it to match twitch's naming convention and check every time if the first tag is a language, if not then go to the second tag etc.

Another issue that was really hard to diagnose was with hosting. There is a mechanism on twitch that lets you host other people's stream when you aren't streaming yourself. So I encountered a problem that sometimes between the time that I get the link and go the link to scrape the data, the streamer would end his/hers stream and host somebody else. In that case there was no HTML code for the viewers count and my script crashed (which is really bad, as you know from the previous paragraph). 

Fortunately I learned how to handle errors and wait for certain elements to load using selenium so all of the issues above could me mitigated.

## The result
The result of my web scraping project is data that is accurate and complete and also a lot of incomplete data. The script didn't work correctly a couple of times and it collected data 3 times a day sometimes instead of 48. It also crashed a couple of times because of chrome updates not being installed and I didn't notice for a few days. That led to gaps that couldn't be overlooked. All in all, I have complete data from 2020-04-15 to 2020-05-12 so approximately a month's worth of data.

I invite you to check out a simple analysis I made and to look on the raw data yourself! 
