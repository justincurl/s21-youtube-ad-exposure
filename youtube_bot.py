from selenium import webdriver
import time
import datetime
import os
import re
import sys
import enum
from multiprocessing import Process
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import randint
from selenium.common.exceptions import TimeoutException
import psycopg2
from bs4 import BeautifulSoup

class Behaviors(enum.Enum):
    Negative = 'NEGATIVE'
    Neutral = 'NEUTRAL'
    Positive = 'POSITIVE'

class Ads(enum.Enum):
    Pre_Video = 'PRE_VIDEO'
    Overlay = 'OVERLAY'
    In_Video = 'IN_VIDEO'


def handle_video_ad(driver, ad_element, behavior_type):
    ad_soup = BeautifulSoup(ad_element.get_attribute("innerHTML"), "html.parser")
    try:
        advertiser = ad_soup.find("button", class_="ytp-ad-button ytp-ad-visit-advertiser-button ytp-ad-button-link")['aria-label']
    except TypeError as e:
        return handle_video_ad(driver, WebDriverWait(driver, 5, poll_frequency = 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".video-ads.ytp-ad-module"))), behavior_type)
    except:
        advertiser = 'N/A'

    ad_text = ad_soup.get_text()
    why_this_ad_index = ad_text.find('Why this ad?')
    
    if ad_text[why_this_ad_index - 5].isnumeric():
        ad_length = ad_text[why_this_ad_index - 5: why_this_ad_index]
    else:
        ad_length = ad_text[why_this_ad_index - 4: why_this_ad_index]

    pt = datetime.datetime.strptime(ad_length, "%M:%S")
    ad_length_seconds = pt.second + pt.minute*60

    if ad_text[why_this_ad_index - 7] == '2':
        num_ads = 2
    else:
        num_ads = 1

    preview_or_skip = WebDriverWait(driver, 5, poll_frequency = 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ytp-ad-player-overlay-skip-or-preview"))).get_attribute("innerHTML")
    preview_soup = BeautifulSoup(preview_or_skip, "html.parser")

    time_until_action = ad_length_seconds + 1

    if 'will' in preview_soup.get_text():
        try:
            time_until_action = int(re.search(r'\d+', preview_soup.get_text()).group())
        except:
            pass  
        skippable = False
    else:
        skippable = True

    
    if behavior_type == "NEGATIVE" and skippable:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ytp-ad-skip-button.ytp-button"))).click()
    elif behavior_type == "NEUTRAL" and skippable:
        if randint(0, 1):
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ytp-ad-skip-button.ytp-button"))).click()
        else:
            time.sleep(time_until_action)
    else:
        time.sleep(time_until_action)

    return (num_ads, skippable, ad_length_seconds, advertiser)


def initial_ads(driver, behavior_type):
    try:
        initial_ads = True
        ad_found = False
        ad_info = []
        while initial_ads:
            try: 
                ad_element = WebDriverWait(driver, 5, poll_frequency = 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".video-ads.ytp-ad-module")))
                ad_info.append(handle_video_ad(driver, ad_element, behavior_type))
            except TimeoutException:
                initial_ads = False
                return ad_info

    except Exception as e:
        print(e)
        print(ad_element.get_attribute('innerHTML'))


def handle_ad_overlay(ad_soup, driver):
    print('overlay ad detected')
    initial_time = time.time()
    try:
        WebDriverWait(driver, 300, poll_frequency=1).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".video-ads.ytp-ad-module")))
    except:
        return round(time.time() - initial_time)


def listen_for_ad(driver, t_video_end, t_end, video_info, username, behavior_type, logged_in, cursor):
    print('listening for ads')
    while time.time() < t_video_end:
        if time.time() >= t_end:
            return True
        try:
            ad_element = WebDriverWait(driver, 3, poll_frequency=1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".video-ads.ytp-ad-module")))
            ad_soup = BeautifulSoup(ad_element.get_attribute("innerHTML"), "html.parser")
            if ad_soup.find('div', class_='ytp-ad-overlay-container'):
                ad_length_seconds = handle_ad_overlay(ad_soup, driver)
                insert_ad_entry(username, behavior_type, video_info[0], video_info[1], 1, None, ad_length_seconds, None, Ads.Overlay.name, logged_in, cursor)
            else:
                ad_info = handle_video_ad(driver, ad_element, behavior_type)
                insert_ad_entry(username, behavior_type, video_info[0], video_info[1], ad_info[0], ad_info[1], ad_info[2], ad_info[3], Ads.In_Video.name, logged_in, cursor)
        except Exception as e:
            pass
    return False
            

def collect_video_info(driver):
    video_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".title.style-scope.ytd-video-primary-info-renderer"))).get_attribute('innerHTML')
    video_soup = BeautifulSoup(video_element, "html.parser")
    print('video info: ', video_soup.get_text())
    
    video_length_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ytp-time-display"))).get_attribute('innerHTML')
    video_length_soup = BeautifulSoup(video_length_element, "html.parser")

    time_str = video_length_soup.find('span', class_="ytp-time-duration").get_text()
    if len(time_str) > 5:
        pt = datetime.datetime.strptime(time_str, "%H:%M:%S")
        video_length_seconds = pt.second + pt.minute*60 + pt.hour*3600
    else:
        pt = datetime.datetime.strptime(time_str, "%M:%S")
        video_length_seconds = pt.second + pt.minute*60

    return (video_soup.get_text(), video_length_seconds)


def insert_ad_entry(username, user_behavior, video_title, video_length_seconds, num_ads, skippable, ad_length_seconds, advertiser, ad_type, logged_in, cursor):
    
    insert_statement = """
    INSERT INTO ads(username, user_behavior, video_title, video_length_seconds, num_ads, skippable, ad_length_seconds, advertiser, ad_type, logged_in)
    VALUES ('{}', '{}', '{}', {}, {}, {}, {}, '{}', {});
    """.format(username, user_behavior, video_title, video_length_seconds, num_ads, skippable, ad_length_seconds, advertiser, ad_type, logged_in)

    # print(insert_statement)

    cursor.execute(insert_statement)


def find_next_video(driver):
    next_video_string = "ytd-compact-video-renderer.style-scope:nth-child({0})".format(randint(1, 7))
    try: 
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, next_video_string))).click()
    except:
        return find_next_video(driver)

def click_elems(elems):
    try:
        elems[randint(1, min(len(elems), 7))].click()
    except:
        click_elems(elems)

def run_bot(driver, cursor, behavior_type, username, logged_in):
    print('selecting video...')
    elem = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "style-scope ytd-rich-item-renderer"))
    )
    elems = driver.find_elements_by_class_name("style-scope ytd-rich-item-renderer")
    
    click_elems(elems)

    'video selected'

    t_end = time.time() + 60 * 2
    while time.time() < t_end:

        ad_info = initial_ads(driver, behavior_type)
        'initial ad info processed'

        video_info = collect_video_info(driver)
        'video info collected'

        time_til_next_seconds = video_info[1] - 1

        if len(ad_info) == 2:
            num_ads = ad_info[0][0]
            insert_ad_entry(username, behavior_type, video_info[0], video_info[1], num_ads, ad_info[0][1], ad_info[0][2], ad_info[0][3], Ads.Pre_Video.name, logged_in, cursor)
            insert_ad_entry(username, behavior_type, video_info[0], video_info[1], ad_info[1][0], ad_info[1][1], ad_info[1][2], ad_info[1][3], Ads.Pre_Video.name, logged_in, cursor)
        
        elif len(ad_info) == 1:
            num_ads = ad_info[0][0]
            insert_ad_entry(username, behavior_type, video_info[0], video_info[1], num_ads, ad_info[0][1], ad_info[0][2], ad_info[0][3], Ads.Pre_Video.name, logged_in, cursor)

        else:
            num_ads = 0
            insert_ad_entry(username, behavior_type, video_info[0], video_info[1], num_ads, None, None, None, None, logged_in, cursor)

        print('ad information inserted into database')

        if num_ads == 0:
            time_til_next_seconds -= 5
        
        t_video_end = time.time() + randint(time_til_next_seconds//2, time_til_next_seconds)

        session_ended = listen_for_ad(driver, t_video_end, t_end, video_info, username, behavior_type, logged_in, cursor)
        
        if session_ended:
            driver.close()
            print("40 Minutes has passed")
            return

        find_next_video(driver)
           
        print('New Video')
    
    driver.close()
    print("40 Minutes has passed")
    return
        