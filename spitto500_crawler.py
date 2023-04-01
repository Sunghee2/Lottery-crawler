from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

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
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get('https://www.dhlottery.co.kr/store.do?method=topStore&pageGubun=SP500')

# 결과를 저장하여 보여줄 리스트이다.
result = []
result_second = []

# 262회차부터 852회차까지 실행하기 위한 for문이다.
for i in range(5, 41):
    # select id가 drwNo이고 그 밑의 해당 회차 option을 선택한다.
    path = '//*[@id="drwNo"]/option[text()="' + str(i) + '"]'
    try:
        driver.find_element(by=By.XPATH, value=path).click()
    except NoSuchElementException:
        print(i, "pass")
        continue
    # 회차를 선택한 후 조회버튼을 클릭한다.
    driver.find_element(By.ID, 'searchBtn').click()

    # webdriver의 페이지 내용을 beautifulsoup으로 가져온다.
    content = BeautifulSoup(driver.page_source, 'html.parser')
    # class가 tbl_data_col인 table이 처음 있는 것을 찾고(1등 배출점) 그 밑의 tr tag를 모두 찾는다.
    list_items = content.find('table', {'class' : 'tbl_data_col'}).findAll('tr')

    # 1등이 없는 회차가 있어서 len(list_items) > 2 조건을 넣어준다.
    if len(list_items) >= 2:
        # 위에서 받은 tr tag를 for문으로 돈다.
        for j in range(1, len(list_items)):
            # tr tag 밑에 td tag를 찾는다.
            td_list = list_items[j].findAll('td')
            # td 2번째가 구분(자동, 반자동, 수동)이기 때문에 텍스트를 받아오고 텍스트에 의미없는 공백이 많았기 때문에 strip()을 해주었다.
            # 위에서 받은 mode가 자동인 것만 수집한다.
            # if mode == '자동':
                # mode가 자동이면 td 첫 번째에 있는 상호명과 td 세 번째에 있는 소재지를 받아온다.
            if(td_list[0].text != '1'):
                break
            shop = td_list[1].text.strip()
            location = td_list[2].text.strip().replace('(', '').replace(')', '').replace(',', '')
            print(1, ': ', i, ' ',  location)
            
            payload['query'] = location
            res = requests.get(url, headers=headers, params=payload)
            res_data = res.json()
            if location is None or location == '' or len(res_data['addresses']) < 1:
                cur.execute("""INSERT INTO sp500 (shop, location, ranking, round) VALUES ("%s", "%s", "%d", "%d")""" % (shop, location, 1, i))
            else:
                print(float(res_data['addresses'][0]['x']), float(res_data['addresses'][0]['y']))
                # 상호명과 소재지를 배열에 넣어준다.
                # result.append({'shop':shop, 'location':location, 'mode': mode, 'rank': '1'})
                cur.execute("""INSERT INTO sp500 (shop, location, ranking, round, x, y) VALUES ("%s", "%s", "%d", "%d", "%f", "%f")""" % (shop, location, 1, i, float(res_data['addresses'][0]['x']), float(res_data['addresses'][0]['y'])))
                conn.commit()

    # 2등
    # pagination = driver.find_element(By.CLASS_NAME, 'paginate_common').find_elements(By.TAG_NAME, 'a')
    # for index, page in enumerate(pagination):
    #     driver.find_element(By.CLASS_NAME, 'paginate_common').find_elements(By.TAG_NAME, 'a')[index].click()
    second_content = BeautifulSoup(driver.page_source, 'html.parser')
    second_list_items = second_content.findAll('table', {'class' : 'tbl_data_col'})[1].findAll('tr')

    if len(second_list_items) >= 2:
        # 위에서 받은 tr tag를 for문으로 돈다.
        for j in range(1, len(second_list_items)):
            
            # tr tag 밑에 td tag를 찾는다.
            second_td_list = second_list_items[j].findAll('td')
            if(second_td_list[0].text != '1'):
                break
            shop = second_td_list[1].text.strip()
            location = second_td_list[2].text.strip()
            print(2, ': ', i, ' ',  location)

            payload['query'] = location
            res = requests.get(url, headers=headers, params=payload)
            res_data = res.json()
            if len(res_data['addresses']) < 1:
                cur.execute("""INSERT INTO sp500 (shop, location, ranking, round) VALUES ("%s", "%s", "%d", "%d")""" % (shop, location, 1, i))
            else:
                print(float(res_data['addresses'][0]['x']), float(res_data['addresses'][0]['y']))
                # 상호명과 소재지를 배열에 넣어준다.
                # result_second.append({'shop':shop, 'location':location, 'rank': '2'})
                cur.execute("""INSERT INTO sp500 (shop, location, ranking, round, x, y) VALUES ("%s", "%s", "%d", "%d", "%f", "%f")""" % (shop, location, 2, i, float(res_data['addresses'][0]['x']), float(res_data['addresses'][0]['y'])))
                conn.commit()

cur.close()