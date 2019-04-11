from selenium import webdriver
from bs4 import BeautifulSoup

# 다운받은 크롬드라이버를 불러와서 사이트를 실행한다.
driver = webdriver.Chrome('./chromedriver')
driver.get('https://www.dhlottery.co.kr/store.do?method=topStore&pageGubun=L645')

# 결과를 저장하여 보여줄 리스트이다.
result = []

# 262회차부터 852회차까지 실행하기 위한 for문이다.
for i in range(262, 852):
    print(i)
    # select id가 drwNo이고 그 밑의 해당 회차 option을 선택한다.
    path = '//*[@id="drwNo"]/option[text()="' + str(i) + '"]'
    driver.find_element_by_xpath(path).click()
    # 회차를 선택한 후 조회버튼을 클릭한다.
    driver.find_element_by_id('searchBtn').click()

    # webdriver의 페이지 내용을 beautifulsoup으로 가져온다.
    content = BeautifulSoup(driver.page_source, 'html.parser')
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
                # 상호명과 소재지를 배열에 넣어준다.
                result.append({'shop':shop, 'location':location})

print(result)