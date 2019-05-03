import requests
from bs4 import BeautifulSoup
import pymysql
import sys

REGION = 'ap-northeast-2a'

rds_host = 'endpoint'
username = 'user_name'
password = 'user_password'
db_name = 'db_name'

def save_data():
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

    # insert시 한글이 깨지지 않기 위해 넣어준다.
    cur = conn.cursor()
    cur.execute('set names utf8')
    conn.commit()

    page = requests.get('https://www.dhlottery.co.kr/store.do?method=topStore&pageGubun=L645')

    # webdriver의 페이지 내용을 beautifulsoup으로 가져온다.
    content = BeautifulSoup(page.content, 'html.parser')
    # class가 tbl_data_col인 table이 처음 있는 것을 찾고(1등 배출점) 그 밑의 tr tag를 모두 찾는다.
    list_items = content.find('table', {'class' : 'tbl_data_col'}).findAll('tr')

    # 1등이 없는 회차가 있어서 len(list_items) > 2 조건을 넣어준다.
    if len(list_items) > 2:
        # 위에서 받은 tr tag를 for문으로 돈다.
        for j in range(1, len(list_items)):
            # tr tag 밑에 td tag를 찾는다.
            td_list = list_items[j].findAll('td')
            # td 2번째가 구분(자동, 반자동, 수동)이기 때문에 텍스트를 받아오고 텍스트에 의미없는 공백이 많았기 때문에 strip()을 해주었다.
            mode = td_list[2].text.strip()
            # 위에서 받은 mode가 자동인 것만 수집한다.
            if mode == '자동':
                # mode가 자동이면 td 첫 번째에 있는 상호명과 td 세 번째에 있는 소재지를 받아온다.
                shop = td_list[1].text.strip()
                location = td_list[3].text.strip()
                # 회차와 상호명 소재지를 lottery table에 insert하고 commit()하여 넣어준다.
                cur.execute("""INSERT INTO lottery (shop, location) VALUES ("%s", "%s")""" % (shop, location))
                conn.commit()

    cur.close()

def main(event, context):
    save_data()
