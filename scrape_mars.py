import numpy as np
import pandas as pd
from splinter import Browser
from selenium import webdriver
from bs4 import BeautifulSoup   
import requests
import time
import pymongo
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'C:/webdrivers/chromedriver'}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    """ Function: Main scrape functionality
        Calls other functions
        Parameters: None
        Returns: combined mars_data dictionary """

    mars_data = {}
    mars_data["news_data"] = marsNewsData()
    mars_data["featured_image_url"] = marsFeaturedImageURL()
    mars_data["mars_weather"] = marsWeather()
    mars_data["mars_facts"] = marsFacts()
    mars_data["mars_hemispheres"] = marsHemisphereImageURLs()

    # return mars_data dict
    return mars_data


def marsNewsData():
    """ Mars news data scraping functionality """

    browser = init_browser()
    news_data = {}
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    time.sleep(5)

    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    news_title = soup.find(class_='content_title').find('a').text
    news_p = soup.find(class_='article_teaser_body').text

    news_data["news_title"] = news_title
    news_data["paragraph"] = news_p

    browser.quit()

    return news_data


def marsFeaturedImageURL():
    """ Function: Mars featured image data scraping functionality
        Scrapes JPL news site @ jpl_url below
        Parameters: None
        Returns: featured_image_url string """

    browser = init_browser()

    url2 = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    base = 'https://www.jpl.nasa.gov'
    browser.visit(url2)
    time.sleep(5)
    # HTML Object
    html2 = browser.html
    # Parse HTML with Beautiful Soup
    soup2 = BeautifulSoup(html2, 'html.parser')

    banner_info = soup2.findAll('article',{'class':['carousel_item']})
    picture = [banner.get('style') for banner in banner_info]
    append = picture[0].replace("background-image: url('","")
    append = append.replace("');","")
    pic_url = base + append

    browser.quit()

    return pic_url

def marsWeather():
    """ Function: Mars twitter weather data scraping functionality
        Scrapes Twitter for weather news @ tweet_url below
        Parameters: None
        Returns: mars_weather string """

    browser = init_browser()

    url = 'https://twitter.com/marswxreport?lang=en' 
    data = requests.get(url)
    time.sleep(5)

    all_tweets = []
    html = BeautifulSoup(data.text, 'html.parser')
    timeline = html.select('#timeline li.stream-item')
    for tweet in timeline:
            tweet_text = tweet.select('p.tweet-text')[0].get_text()
            if "sol" in tweet_text:
                all_tweets.append(tweet_text)
    
    
    mars_weather = all_tweets[0]
          
    browser.quit()

    return mars_weather


def marsFacts():
    """ Function: Mars facts data scraping functionality
        Scrapes Space-Facts site @ facts_url below
        Parameters: None
        Returns facts_table string (HTML) """

    url3 = 'https://space-facts.com/mars/'
    tables = pd.read_html(url3)
    df = tables[0]
    df.columns = ['Feature', 'Notes']
    df.set_index('Feature', inplace=True)
    html_table = df.to_html()
    html_table = html_table.replace('\n', '')
    facts_table = html_table 
    

    return facts_table

def marsHemisphereImageURLs():
    """ Function: Mars hemispheres image data scraping functionality
        Scrapes USGS site @ usgs_url below
        Parameters: None
        Returns: hemisphere_image_urls list """

    browser = init_browser()

    url4 = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    burl = 'https://astrogeology.usgs.gov'
    browser.visit(url4)
    time.sleep(5)

    titles = []
    linklist = []
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    t = soup.find_all('h3')
    for x in t:
        titles.append(x.text)

    for i in titles:
        browser.click_link_by_partial_text(i)
        # HTML object
        html = browser.html
        # Parse HTML with Beautiful Soup
        soup = BeautifulSoup(html, 'html.parser')
        # Retrieve all elements that contain book information
        u = soup.find('img', class_ = 'wide-image')
        linklist.append(burl + u["src"])
        browser.click_link_by_partial_text('Back')
    
    keys  = ["title", "img_url"]
    hemisphere_image_urls = [dict(zip(keys,row)) for row in zip(titles,linklist)]

    browser.quit()

    return hemisphere_image_urls