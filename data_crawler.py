from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait       
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import time
import requests
import pymysql
import sys

REGION = 'ap-northeast-2a'

rds_host = 'localhost'
username = 'root'
db_name = 'lottery'

# pymysql 라이브러리를 사용하여 mysql + aws rds에 연결한다.
conn = pymysql.connect(
    host=rds_host, 
    port=3306,
    user=username, 
    passwd=password, 
    db=db_name, 
    charset='utf8',
    connect_timeout=5
)

headers = {
    'X-NCP-APIGW-API-KEY-ID': 'l57xykhrcx',
    'X-NCP-APIGW-API-KEY': 'haOsaZxNOnt7l7XOat0Su9ujvs3zobktcNHYD0Kf'
}

payload = {
    'query': 'null'
}

url = 'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode'

# insert시 한글이 깨지지 않기 위해 넣어준다.
cur = conn.cursor()
cur.execute('set names utf8')
conn.commit()

# 다운받은 크롬드라이버를 불러와서 사이트를 실행한다.
options = webdriver.ChromeOptions()
options.add_extension('extension_5_1_2_0.crx')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver = webdriver.Chrome(options=options)
driver.get('https://data.soledot.com/lottowinstore/fo/lottowinstorelist.sd')

# 결과를 저장하여 보여줄 리스트이다.
result = []
result_second = []

cur_index = 1

while True:
    print(cur_index)
    # webdriver의 페이지 내용을 beautifulsoup으로 가져온다.
    content = BeautifulSoup(driver.page_source, 'html.parser')
    # class가 tbl_data_col인 table이 처음 있는 것을 찾고(1등 배출점) 그 밑의 tr tag를 모두 찾는다.
    list_items = content.find('table', {'class' : 'table'}).findAll('tr')

    # 1등이 없는 회차가 있어서 len(list_items) > 2 조건을 넣어준다.
    if len(list_items) >= 2:
        # 위에서 받은 tr tag를 for문으로 돈다.
        for j in range(1, len(list_items)):
            # tr tag 밑에 td tag를 찾는다.
            td_list = list_items[j].findAll('td')
            # td 2번째가 구분(자동, 반자동, 수동)이기 때문에 텍스트를 받아오고 텍스트에 의미없는 공백이 많았기 때문에 strip()을 해주었다.
            mode = td_list[2].text.strip()
            # 위에서 받은 mode가 자동인 것만 수집한다.
            # if mode == '자동':
                # mode가 자동이면 td 첫 번째에 있는 상호명과 td 세 번째에 있는 소재지를 받아온다.
            round = int(td_list[0].text)
            shop = td_list[1].text.strip()
            location = td_list[5].text.strip()
            rank = int(td_list[3].text)

            payload['query'] = location
            res = requests.get(url, headers=headers, params=payload)
            res_data = res.json()
            print(res_data, location)
            if location is None or location == '' or len(res_data['addresses']) < 1:
                cur.execute("""INSERT INTO lottery (shop, location, ranking, round) VALUES ("%s", "%s", "%d", "%d")""" % (shop, location, rank, round))
            else:
                print(float(res_data['addresses'][0]['x']), float(res_data['addresses'][0]['y']))
                # 상호명과 소재지를 배열에 넣어준다.
                # result_second.append({'shop':shop, 'location':location, 'rank': '2'})
                cur.execute("""INSERT INTO lottery (shop, location, ranking, round, x, y) VALUES ("%s", "%s", "%d", "%d", "%f", "%f")""" % (shop, location, rank, round, float(res_data['addresses'][0]['x']), float(res_data['addresses'][0]['y'])))
                conn.commit()

    time.sleep(1)
    # ad_root = driver.find_element(By.XPATH, "//div[@class='grippy-host']")
    # shadow_ad_root = driver.execute_script('return arguments[0].shadowRoot', ad_root)
    # shadow_ad_root.find_element(By.XPATH, "//svg").click()
    # time.sleep(1)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='page-item active']//following-sibling::li"))).click()
    # driver.find_elements(By.XPATH, )[-1].click()
    next_index = driver.find_element(By.XPATH, "//li[@class='page-item active']/a").text

    if cur_index != next_index: 
        cur_index = next_index
        continue
    break

cur.close()