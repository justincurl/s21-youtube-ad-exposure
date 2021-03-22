from selenium import webdriver
import time
import datetime
import os
import re
from multiprocessing import Process
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import randint
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
# import psycopg2

def find_preview_or_skip(driver):
    try: 
        preview_or_skip = WebDriverWait(driver, 5, poll_frequency = 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ytp-ad-player-overlay-skip-or-preview"))).get_attribute("innerHTML")
        preview_soup = BeautifulSoup(preview_or_skip, "html.parser")
        preview_digit = re.search(r'\d+', preview_soup.get_text()).group()
    except:
        return find_preview_or_skip(driver)
    return preview_soup


def handle_video_ad(driver, ad_element):
    ad_soup = BeautifulSoup(ad_element.get_attribute("innerHTML"), "html.parser")
    try:
        advertiser = ad_soup.find("button", class_="ytp-ad-button ytp-ad-visit-advertiser-button ytp-ad-button-link")['aria-label']
    except Exception as e:
        return handle_video_ad(driver, WebDriverWait(driver, 5, poll_frequency = 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".video-ads.ytp-ad-module"))))
    
    print('advertiser: ', advertiser)
    
    ad_text = ad_soup.get_text()
    why_this_ad_index = ad_text.find('Why this ad?')
    
    if ad_text[why_this_ad_index - 5].isnumeric():
        ad_length = ad_text[why_this_ad_index - 5: why_this_ad_index]
    else:
        ad_length = ad_text[why_this_ad_index - 4: why_this_ad_index]

    pt = datetime.datetime.strptime(ad_length, "%M:%S")
    ad_length_seconds = pt.second + pt.minute*60

    print('ad_length', ad_length)

    if ad_text[why_this_ad_index - 7] == '2':
        num_ads = 2
    else:
        num_ads = 1

    print('num_ads: ', num_ads)
    
    preview_soup = find_preview_or_skip(driver)

    if 'will' in preview_soup.get_text():
        print('time until video: ', re.search(r'\d+', preview_soup.get_text()).group())
        skippable = False
    else:
        skippable = True

    print('skippable: ', skippable)

    if skippable:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".ytp-ad-skip-button.ytp-button"))).click()
    
    time.sleep(ad_length_seconds + 1)

    return num_ads


def initial_ads(driver):
    try:
        initial_ads = True
        ad_found = False
        while initial_ads:
            try: 
                ad_element = WebDriverWait(driver, 5, poll_frequency = 1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".video-ads.ytp-ad-module")))
                num_ads = handle_video_ad(driver, ad_element)
                ad_found = True
            except TimeoutException:
                initial_ads = False
                if not ad_found:
                    num_ads = 0
                    print('num_ads', num_ads)
                return num_ads
    except Exception as e:
        print(e)
        print(ad_element.get_attribute('innerHTML'))


def handle_ad_overlay(ad_soup):
    print('ad overlay: ')

    initial_time = time.time()

    WebDriverWait(driver, 120, poll_frequency=1).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".video-ads.ytp-ad-module")))
    
    print('ad disappeared: ', time.time() - initial_time)


def listen_for_ad(driver, t_video_end, t_end):
    while time.time() < t_video_end:
        if time.time() >= t_end:
            sys.exit()
        try:
            ad_element = WebDriverWait(driver, 3, poll_frequency=1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".video-ads.ytp-ad-module")))
            ad_soup = BeautifulSoup(ad_element.get_attribute("innerHTML"), "html.parser")
            if ad_soup.find('div', class_='ytp-ad-overlay-container'):
                handle_ad_overlay(ad_soup)
            else:
                handle_video_ad(driver, ad_element)
        except Exception as e:
            pass
            

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

    print('video length: ', time_str)
    return video_length_seconds


def find_next_video(driver):
    next_video_string = "ytd-compact-video-renderer.style-scope:nth-child({0})".format(randint(1, 7))
    try: 
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, next_video_string))).click()
    except:
        return find_next_video(driver)


def run_skip_bot(driver):
    driver.get("http://www.youtube.com")
    elem = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "style-scope ytd-rich-item-renderer"))
    )
    elems = driver.find_elements_by_class_name("style-scope ytd-rich-item-renderer")
    
    elems[randint(0, 8)].click()

    t_end = time.time() + 60 * 50
    while time.time() < t_end:

        num_ads = initial_ads(driver)

        time_til_next_seconds = collect_video_info(driver)

        if num_ads == 0:
            time_til_next_seconds -= 5
        
        t_video_end = time.time() + randint(time_til_next_seconds//2, time_til_next_seconds)

        # cur.execute(sql, (vendor_name,))

        listen_for_ad(driver, t_video_end, t_end)

        find_next_video(driver)
           
        print('=====================New Video=====================')
        
    driver.close()


def account_sign_in(driver, username, password):
    driver.get("https://www.youtube.com/")

    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ytd-button-renderer.style-scope:nth-child(3)"))).click()
    
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='identifierId']"))).send_keys(username)
    time.sleep(randint(10, 20)/10)
    
    if randint(0, 1):
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button"))).click()
    else:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='identifierId']"))).send_keys(Keys.RETURN)
    time.sleep(randint(10, 20)/10)
    
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input"))).send_keys(password)
    time.sleep(randint(10, 20)/10)

    if randint(0, 1):
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='passwordNext']"))).click()
    else:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input"))).send_keys(Keys.RETURN)
    time.sleep(randint(10, 20)/10)

    

if __name__ == '__main__':
    # set up browser
    # DATABASE_URL = os.environ['DATABASE_URL']

    # conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    # cur = conn.cursor()

    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
    driver = webdriver.Firefox(firefox_profile=firefox_profile)

    # account_sign_in(driver, 'wj8653032@gmail.com', 'ZpxeCKQCVkZ9Rne')

    run_skip_bot(driver)