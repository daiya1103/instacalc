from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from selenium.webdriver.common.action_chains import ActionChains

import os
from PIL import Image
import openpyxl
from styleframe import StyleFrame
import pandas as pd
import re
import shutil
import pathlib
import sys
import math

# インスタグラムID or EMAIL, PASSWORD
USERNAME = 'daishin298@gmail.com'
PASSWORD = 'tY/b8pow'

# ぶっこぬき対象インスタID
IDS = ['a5y1a3k', 'meruko.buppan']



# 注！！！！以下おさわり厳禁！！！！
CUR_DIR = str(pathlib.Path(sys.argv[0]).resolve().parent)

EMAIL_INPUT = '#loginForm > div > div:nth-child(1) > div > label > input'
PASS_INPUT = '#loginForm > div > div:nth-child(2) > div > label > input'
LOGIN_BTN = '#loginForm > div > div:nth-child(3) > button'

ALL_POST = 'main > div > div:nth-of-type(3) > div > div > div > a'
THUMBNAIL = 'img'
NEXT_BTN = 'div._aaqg > button'

# ARTICLE_THUMB = 'article > div > div:nth-of-type(1)'
ACCESS = 'span[style="line-height: 18px;"]'
LIKE_VALUE = ACCESS + ' > span'
SCROLL = 'div[style="height: 356px; overflow: hidden auto;"]'
LIKE_PEOPLE = 'div[style="height: 356px; overflow: hidden auto;"] > div > div > div > div > div > div > div > div > div > div > a'
URL = 'article > div > div:nth-of-type(2) > div > div> div:nth-of-type(2) > div:nth-of-type(2) a'
DATE = ACCESS + ' > time'

def word_regex(word):
        code_regex = re.compile(
            "[!\'#$%&'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]"
        )
        word = code_regex.sub('', word)

        return word

def setup_webdriver():
    options = Options()
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    )
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    chrome_service = service.Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(
        service=chrome_service,
        options=options,
    )

    return driver

def scrape():
    driver = setup_webdriver()
    driver.implicitly_wait(3)

    driver.get('https://www.instagram.com/')

    sleep(1)

    email_elm = driver.find_element(By.CSS_SELECTOR, EMAIL_INPUT)
    email_elm.send_keys(USERNAME)

    sleep(1)

    pass_elm = driver.find_element(By.CSS_SELECTOR, PASS_INPUT)
    pass_elm.send_keys(PASSWORD)

    sleep(1)

    login_btn = driver.find_element(By.CSS_SELECTOR, LOGIN_BTN)
    login_btn.click()

    sleep(5)

    driver.get('https://www.instagram.com/reel/C1X1lL2pifP/')
    sleep(1)

    access_elms = driver.find_elements(By.CSS_SELECTOR, ACCESS)

    if len(access_elms) >= 3:
        content = access_elms[-3].text
        # 投稿日抽
        date = driver.find_element(By.CSS_SELECTOR, DATE).get_attribute('title')
        access_elms[-1].click()
        sleep(1)
        old_len = 0
        new_len = 1
        like_url_list = []
        while old_len < new_len:
            old_len = len(like_url_list)
            likes = driver.find_elements(By.CSS_SELECTOR, LIKE_PEOPLE)
            for like_a in likes:
                like_url = like_a.get_attribute('href')
                print(like_url)
                if like_url not in like_url_list:
                    like_url_list.append(like_url)
            new_len = len(like_url_list)

            scroll_element = driver.find_element(By.CSS_SELECTOR, SCROLL)
            current_scroll_position = driver.execute_script("return arguments[0].scrollTop;", scroll_element)
            print(current_scroll_position)
            actions = ActionChains(driver)
            actions.move_to_element(scroll_element).perform()
            scroll_script = """
                arguments[0].scrollTop = arguments[1];
            """
            driver.execute_script(scroll_script, scroll_element, current_scroll_position + 356)
            sleep(1)
        like = new_len
        print(like)
        sleep(1)

        driver.quit()

scrape()