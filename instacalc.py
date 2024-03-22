from time import sleep
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service
from selenium.webdriver.chrome.options import Options
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
IDS = ['marina.mercari', '_realiser7aya', 'inport_meru']



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

    sleep(10)

    for id in IDS:
        driver.get(f'https://www.instagram.com/{id}/')

        url_list = []

        i = 0
        url_len_old = 0
        url_len_new = 1

        while len(url_list) < 50 and url_len_old < url_len_new :
            sleep(2)
            url_len_old = len(url_list)
            posts = driver.find_elements(By.CSS_SELECTOR, ALL_POST)
            for post in posts:
                sleep(0.1)
                url = post.get_attribute('href')
                rep = url.split('/')[-2]
                if url not in url_list:
                    url_list.append(url)
                    thumbnail = post.find_element(By.CSS_SELECTOR, 'img')
                    img_name = f'{rep}.png'
                    IMG_PATH = CUR_DIR + '/thumbnail/' + img_name
                    with open(IMG_PATH, "wb") as f:
                        f.write(thumbnail.screenshot_as_png)
            url_len_new = len(url_list)

        article_datas = []

        for url in url_list:
            try:
                driver.get(url)
                sleep(1)

                access_elms = driver.find_elements(By.CSS_SELECTOR, ACCESS)

                if len(access_elms) >= 3:
                    # いいね数抽出
                    content = access_elms[-3].text
                    # 投稿日抽
                    date = driver.find_element(By.CSS_SELECTOR, DATE).get_attribute('title')
                    rep = url.split('/')[-2]
                    try:
                        like = int(driver.find_element(By.CSS_SELECTOR, LIKE_VALUE).text)
                    except:
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
                                if like_url not in like_url_list:
                                    like_url_list.append(like_url)
                            new_len = len(like_url_list)

                            scroll_element = driver.find_element(By.CSS_SELECTOR, SCROLL)
                            current_scroll_position = driver.execute_script("return arguments[0].scrollTop;", scroll_element)
                            actions = ActionChains(driver)
                            actions.move_to_element(scroll_element).perform()
                            scroll_script = """
                                arguments[0].scrollTop = arguments[1];
                            """
                            driver.execute_script(scroll_script, scroll_element, current_scroll_position + 356)
                            sleep(1)
                        like = new_len
                    sleep(1)
                    article_data = {
                        'サムネイル': '',
                        'URL': url,
                        '投稿日': date,
                        'いいね': like,
                        '内容': content,
                        '投稿ID': rep,
                    }

                    article_datas.append(article_data)
            except Exception as e: 
                print(url)
                print(e)
                pass

        id = word_regex(id)

        XLSX_PATH = CUR_DIR + '/result/' + id + '.xlsx'
        article_df = pd.DataFrame(article_datas)
        with StyleFrame.ExcelWriter(XLSX_PATH) as writer:
            article_sf = StyleFrame(article_df)
            article_sf.set_column_width(columns=1, width=12.5)
            article_sf.set_column_width(columns=2, width=45)
            article_sf.set_column_width(columns=3, width=28)
            article_sf.set_column_width(columns=4, width=9)
            article_sf.set_column_width(columns=5, width=60)
            article_sf.set_column_width(columns=6, width=32)
            article_sf.set_row_height(
                rows=list(range(2, len(article_datas) + 2)), height=75
            )
            article_sf.to_excel(writer, sheet_name=id, index=None)

        # エクセルデータ変換
        workbook = openpyxl.load_workbook(XLSX_PATH)
        ws = workbook[id]
        for j, article in enumerate(article_datas):
            img_name = f'{article['投稿ID']}.png'
            IMG_PATH = CUR_DIR + '/thumbnail/' + img_name

            img = Image.open(IMG_PATH).resize((100, 100))
            img.save(IMG_PATH)

            img_to_excel = openpyxl.drawing.image.Image(IMG_PATH)
            ws.add_image(img_to_excel, "A" + str(j + 2))
            workbook.save(XLSX_PATH)
        workbook.save(XLSX_PATH)
        shutil.rmtree(CUR_DIR + '/thumbnail')
        os.makedirs(CUR_DIR + '/thumbnail')

    driver.quit()

scrape()