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
import subprocess as sp

def send_username_keys(driver, keys):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='identifierId']"))).send_keys(keys)
    except:
        print('attempt old UI username')
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/div[2]/div[2]/div[1]/form/div/div/div/div/div/input[1]"))).send_keys(keys)

def send_password_keys(driver, keys):
    try:
        print('attempt new UI password: ', keys)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input"))).send_keys(keys)
    except:
        try:
            print('attempt CSS Selector')
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#password > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > input:nth-child(1)'))).send_keys(keys)
        except:
            print('attempt shortened path')
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='password']/div[1]/div/div[1]/input"))).send_keys(keys)

def take_screenshot(driver, image_name):
    driver.save_screenshot(image_name)
    print('screenshot: ' + image_name + ' taken')
    output = sp.getoutput("curl -F \"file=@./{}\" https://file.io".format(image_name))
    print(output)
    print('--------------------------------------------------')
    if os.path.exists(image_name):
        os.remove(image_name)
    else:
        print("The file does not exist") 


def account_sign_in(driver, username, password):
    driver.get("https://www.youtube.com/")
    time.sleep(random.randint(10, 20)/10)
    try: 
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "ytd-button-renderer.style-scope:nth-child(3)"))).click()

        send_username_keys(driver, username)
        time.sleep(random.randint(10, 20)/10)
        print('username sent successfully: ', username)

        send_username_keys(driver, Keys.RETURN)
        time.sleep(random.randint(10, 20)/10)

        send_password_keys(driver, password)
        time.sleep(random.randint(10, 20)/10)
        print('password typed: ', password)

        send_password_keys(driver, Keys.RETURN)
        print('enter typed')
        
        time.sleep(random.randint(30, 40)/10)
        try:
            take_screenshot(driver, username + 'post-login.png')

            txt_file = 'pages.txt'
            with open(txt_file, 'w') as f:
                f.write(driver.page_source)
            f.close()

            output = sp.getoutput("curl -F \"file=@./{}\" https://file.io".format(txt_file))
            print(output)
            print('--------------------------------------------------')
            
            print('clicking on email confirmation')
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div/ul/li[2]/div"))).click()
            time.sleep(random.randint(10, 20)/10)   

            take_screenshot(driver, username + 'post-click.png')

            WebDriverWait(driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='knowledge-preregistered-email-response']"))).send_keys("justincurl13@gmail.com")        
            time.sleep(random.randint(5, 10)/10)  
            
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id='knowledge-preregistered-email-response']"))).send_keys(Keys.RETURN)
            time.sleep(random.randint(20, 30)/10)
            
            print('email confirmed')

            take_screenshot(driver, username + 'post-email-confirmation.png')
            return False
        except:
            return False
        
    except Exception as e:
        print(e)
        return True


def sign_in_verification(driver, username):
    try:
        driver.get("http://www.youtube.com")

        take_screenshot(driver, username + 'post-youtube.png')

        WebDriverWait(driver, 3).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='avatar-btn']"))).click()

        print('user icon clicked')

        time.sleep(random.randint(5, 10)/10)

        username_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[2]/ytd-active-account-header-renderer/div/yt-formatted-string[2]"))).get_attribute("innerHTML")
        print('username found')

        username_soup = BeautifulSoup(username_element, "html.parser")

        time.sleep(random.randint(5, 10)/10)
        
        return username_soup.get_text() == username + '@gmail.com'
    except:
        return False

def run_all_bots():
    users = {
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
        "nakaminuuhazaid":	"POSITIVE",
        "hazerbeigema":	"NEUTRAL",
        "kumatajnah":	"NEGATIVE",
        "sustepoleshaya":	"POSITIVE",
        "jermayanganear":	"NEUTRAL",
        "emarthingspire":	"NEGATIVE",
        "meckangaruso":	"POSITIVE",
        "weilveiserberg": "NEUTRAL",
        "wj8653032":	"NEGATIVE",
        "jinerstamous":	"POSITIVE",
    }

    users_keys = users.keys()
    random.shuffle(list(users_keys))
    for username in users_keys:
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        cursor = conn.cursor()

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'")
        chrome_options.add_argument("--start-maximized")  
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)

        password = os.environ.get(username)

        log_in_failed = account_sign_in(driver, username, os.environ.get(username))
        
        if not log_in_failed:
            logged_in = sign_in_verification(driver, username)
        else:
            logged_in = False

        print("username: ", username, ", logged in: ", logged_in)

        if logged_in:
            youtube_bot.run_bot(driver, cursor, users[username], username, logged_in, conn)
        else:
            youtube_bot.run_bot(driver, cursor, random.choices(["NEUTRAL", "NEGATIVE", "POSITIVE"])[0], username, logged_in, conn)
        
        print("USER: {} Completed".format(username))
        driver.close()
    
        cursor.close()
        conn.close()
