#import dependencies
from splinter import Browser
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
import GetOldTweets3 as got
chrome_path = "/usr/local/bin/chromedriver" #for windows

def init_browser():
    executable_path = {"executable_path": chrome_path}
    return Browser("chrome", **executable_path, headless=True)

def scrape():
    #### Scrape Title and Excerpt from NASA Mars News Site ####
    #use the url and open the browser to that webpage
    browser = init_browser()
    
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)

    time.sleep(1)

    #initialize Beautiful Soup
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    #save the newest article title to variable
    news_title = soup.find_all(class_ = "content_title")[1].get_text()
    #save the newest article excerpt to variable
    news_p = soup.find_all(class_ = "article_teaser_body")[0].get_text()


    #### Visit JPL Mars Space Images and pull the Featured Image ####
    #use the url and open the browser to that webpage
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    time.sleep(3)

    #initialize Beautiful Soup
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    #find the image url
    string = soup.find('article', class_= "carousel_item")['style']
    #only use the part of the string that includes the image url
    image = string.split("'")[1]
    #append the url relating to the image to the home site to create a full-page picture url
    new_url = 'https://www.jpl.nasa.gov'

    featured_image_url = new_url + image

    #closes the browser window
    browser.quit()


    #### Scrape Twitter account for Mars weather ####
    #Utilizing GetOldTweets3 for latest Mars weather tweet
    tweetCriteria = got.manager.TweetCriteria().setUsername("marsWxreport").setMaxTweets(1)
    tweet = got.manager.TweetManager.getTweets(tweetCriteria)[0]
    mars_weather = tweet.text


    #### Scrape Mars Facts webpage for Mars information table ####
    #create url
    url = 'https://space-facts.com/mars/'

    #use pandas to read in the table
    mars_tables = pd.read_html(url)
    mars_df = mars_tables[0]
    mars_df = mars_df.rename(columns = {0 : 'description', 1 : 'value'})
    mars_df = mars_df.set_index('description')

    #back to html
    mars_df = mars_df.to_html(classes = 'table')


    #### Scrape USGS Astrogeology site for pictures of Mar's 4 Hemispheres ####
    #set the indexes for where to scrape 
    indexes = [1,3,5,7]

    #empty list for where the img_urls will be recorded
    img_urls = []

    #for loop to start at usgs site, click on the appropriate link then save the image url
    for index in indexes:
        #initializes webdriver
        wd = webdriver.Chrome(executable_path=chrome_path)
        wd.get('https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
        results = wd.find_elements_by_css_selector('a.itemLink')
        #click on the correct link according to the index
        results[index].click()
        #find the image on the next page
        img = wd.find_elements_by_css_selector('img')[5]
        #save the image url to the list
        img_urls.append(img.get_attribute('src'))
        #closes the window
        wd.quit()

    #create the list of dictionaries to hold the corresponding image urls
    hemisphere_image_urls = [
        {"title": "Cerberus Hemisphere", "img_url": "..."},
        {"title": "Schiaparelli Hemisphere", "img_url": "..."},
        {"title": "Syrtis Major Hemisphere", "img_url": "..."},
        {"title": "Valles Marineris Hemisphere", "img_url": "..."},
    ]
    #insert each url into the list of dictionaries
    for x in range(0, len(hemisphere_image_urls)):
        hemisphere_image_urls[x]["img_url"] = img_urls[x]
    
    mars_data = {
            'News_title' : news_title,
            'News_excerpt' : news_p,
            'Featured_image' : featured_image_url,
            'Mars_weather' : mars_weather,
            'Mars_facts' : mars_df,
            'Hemisphere_images_urls' : hemisphere_image_urls
        }

    return(mars_data)
