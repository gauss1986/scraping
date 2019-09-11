from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from time import sleep
import re
import sys
import numpy as np
import pandas as pd

import requests
import string
import itertools
import pickle

import lxml
import html5lib



#Call the driver and open url
url = "https://www.fic.gov.bc.ca/web_listings/mbsblisting.aspx"
driver = webdriver.Chrome(r"C:\Users\mengcem\Documents\chromedriver.exe")
driver.get(url)



#Define an empty dataframe to store the broker information retrieved by web scraper
broker_name = pd.DataFrame()

#The for loop below performs the following tasks:
#Search each of the broker names in add_broker data frame
#Retrieve the broker information if the name can be found
for i in range(add_broker.shape[0]):
    
    #Click different buttons and send broker name to the search bar
    driver.find_element_by_id("optComInd_1").click()
    driver.find_element_by_id("txtSearch").send_keys(add_broker[0][i])
    driver.find_element_by_id("btnSearch").click()
    id = driver.find_element_by_id("lblNoRecords").text
    
    #id refers to the note of "no results found" shown in the browser after search
    #if note exists, we move to the next name as no results returned from the current search 
    if len(id) > 0:
        driver.find_element_by_id("txtSearch").clear()
    
    #if note does not exist, we parse the html results and save them in a table format using beautifulsoup functions
    else:
        html = driver.page_source
        bs = BeautifulSoup(html, 'html.parser')
        table = bs.find('table', id="ComIndList")
        broker_pd = pd.read_html(str(table))
        broker_pd = broker_pd[0]
        driver.find_element_by_id("txtSearch").clear()
    
        #Add table results to the data frame that we defined at the beginning    
        broker_name = broker_name.append(broker_pd, ignore_index = True)



#We take the broker information found above and do another scraping to get broker licensing information
#Define an empty dataframe to store broker licensing information retrieved by web scraper
broker_detail = pd.DataFrame()

for i in range(broker_name.shape[0]):
    
    #Click different buttons and send each name to the search bar
    #Very similar to the first for loop, the difference here is that we will be directed to a new window after the search
    #So we have to switch between windows to search brokers and retrieve the licensing information
    driver.find_element_by_id("txtSearch").send_keys(broker_name.iloc[i])
    driver.find_element_by_id("btnSearch").click()
    driver.find_element_by_link_text(broker_name[0][i]).click()
    driver.switch_to.window(driver.window_handles[1]) #Switch to licensing information window
    
    #Parse the html results and save them in a table format by beautifulsoup functions
    bs = BeautifulSoup(driver.page_source, 'html.parser')
    table = bs.find_all('table', id='EmpList')
    detail_pd = pd.read_html(str(table))
    detail_pd = detail_pd[0]
    detail_pd["Broker"] = ["Agent", broker_name[0][i], "None"]
    broker_detail = broker_detail.append(detail_pd) 
    
    #Close the licensing information window and switch back to the window to search for the next broker name
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    driver.find_element_by_id("txtSearch").clear()

