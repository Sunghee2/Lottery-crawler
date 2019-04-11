from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome('./chromedriver')

driver.get('https://www.dhlottery.co.kr/store.do?method=topStore&pageGubun=L645')
result = []

for i in range(262, 852):
    print(i)
    path = '//*[@id="drwNo"]/option[text()="' + str(i) + '"]'
    driver.find_element_by_xpath(path).click()
    driver.find_element_by_id('searchBtn').click()

    content = BeautifulSoup(driver.page_source, 'html.parser')
    list_items = content.find('table', {'class' : 'tbl_data_col'}).findAll('tr')

    shops = [] 
    for j in range(1, len(list_items)):
        td_list = list_items[j].findAll('td')
        mode = td_list[2].text.strip()
        if mode == '자동':
            shop = td_list[1].text.strip()
            location = td_list[3].text.strip()
            shops.append({'shop':shop, 'location':location})

    # print(shops)
    
    result.append({'round':i, 'shops':shops})
    print(result)



