import youtube_bot
import os
import psycopg2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
import random
from bs4 import BeautifulSoup


def account_sign_in(driver, username, password):
    driver.get("https://www.youtube.com/")
    time.sleep(random.randint(10, 20)/10)
    try: 
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "ytd-button-renderer.style-scope:nth-child(3)"))).click()
        # print('sign in button clicked')

        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='identifierId']"))).send_keys(username)
    
        time.sleep(random.randint(10, 20)/10)
        # print('username typed')

        if random.randint(0, 1):
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button"))).click()
            # print('enter clicked')
        else:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='identifierId']"))).send_keys(Keys.RETURN)
            # print('enter typed')
        time.sleep(random.randint(10, 20)/10)

        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input"))).send_keys(password)
        time.sleep(random.randint(10, 20)/10)
        # print('password typed')

        if random.randint(0, 1):
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='passwordNext']"))).click()
        else:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input"))).send_keys(Keys.RETURN)
        time.sleep(random.randint(10, 20)/10)

        try:
            # print(driver.current_url)
            if driver.current_url == "https://www.youtube.com/":

                WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='avatar-btn']"))).click()
                # print('user icon clicked')

                time.sleep(random.randint(5, 10)/10)
        
                username_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, "/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[2]/ytd-active-account-header-renderer/div/yt-formatted-string[2]"))).get_attribute("innerHTML")
                # print('username found')

                username_soup = BeautifulSoup(username_element, "html.parser")

                time.sleep(random.randint(5, 10)/10)
                
                return username_soup.get_text() == username + '@gmail.com'
            else:
                driver.get("http://www.youtube.com")
                return False
        except:
            driver.get("http://www.youtube.com")
            return False

    except Exception as e:
        print(e)
        driver.get("http://www.youtube.com")
        return False


def run_all_bots():
    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    users = {
        "wj8653032":	"NEUTRAL",
        "noahjameson63":	"NEGATIVE",
        "os339487":	"POSITIVE",
        "liamgarcia235":	"NEUTRAL",
        "js7973973":	"NEGATIVE",
        "matthewanderson325":	"POSITIVE",
        "mireaddhaom":	"NEUTRAL",
        "myrhaquevaed":	"NEGATIVE",
        "muadiibkipchonge":	"POSITIVE",
        "chanihacircuu":	"NEUTRAL",
        "koltchinpoiwante":	"NEGATIVE",
        "qafaritalmaisly":	"POSITIVE",
        "fuhmadmailtowser":	"NEUTRAL",
        "gerranhiplofile":	"NEGATIVE",
        "juhdomanikipcurlro":	"POSITIVE",
        "heishenfleich":	"NEUTRAL",
        "gerbeliamonswariti":	"NEGATIVE",
        "hezermaithal":	"POSITIVE",
        "pershmahnimirstmira":	"NEUTRAL",
        "xermanshihubujudt":	"NEGATIVE",
        "quirkatzarpmunihana":	"POSITIVE",
        "perminuzha":	"NEUTRAL",
        "hyunjinggai":	"NEGATIVE",
        "nakaminuhazai":	"POSITIVE",
    }
    
    for username in users:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")  
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)

        logged_in = account_sign_in(driver, username, os.environ.get(username))
        print(username, logged_in)

        if logged_in:
            youtube_bot.run_bot(driver, cursor, users[username], username, logged_in)
        else:
            youtube_bot.run_bot(driver, cursor, random.choices(["NEUTRAL", "NEGATIVE", "POSITIVE"])[0], username, logged_in)
        
        print("USER: {} Completed".format(username))
    
    cursor.close()
    conn.close()
