from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import requests

def get_html(url):
    try:
        # Chrome 웹 드라이버 실행
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        
        # 웹 페이지 로드
        driver.get(url)
        
        # 페이지가 완전히 로드될 때까지 기다림
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'footer')))
        
        # HTML 가져오기
        html_content = driver.page_source
        
        # # 브라우저 종료
        # driver.quit()
        
        return html_content
    except Exception as e:
        print(f"get_html error : {e}")
        return None  

def get_footer(url):
    try:
        html_content = get_html(url)
        soup = None
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
        else:
            response = requests.get(url)
            # 인코딩 방식 확인
            response.encoding = response.apparent_encoding  # 인코딩 방식 설정
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)

        footer_list = []
        # 풋터 검색
        if soup.find('footer') != None:
            footer_text = soup.find('footer').get_text()
            footer_list.append(footer_text)
        if soup.find('div', class_='footer') != None:
            footer_text2 = soup.find('div', class_='footer').get_text()
            footer_list.append(footer_text2)
        if soup.find('div', id='footer') is not None:
            footer_text3 = soup.find('div', id='footer').get_text()
            footer_list.append(footer_text3)
        if soup is not None:
            footer_text4 = soup.get_text()
            footer_list.append(footer_text4)

        return footer_list
    except Exception as e:
        print(f"error2 : {e}")
    return 'no footer'  

# 메인 함수
if __name__ == "__main__":
    url = 'http://roseonly.co.kr'
    html_content = get_html(url)
    soup = None
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
    else:
        response = requests.get(url)
        # 인코딩 방식 확인
        response.encoding = response.apparent_encoding  # 인코딩 방식 설정
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)

    # 풋터 검색
    footer_list = get_footer(url)

    for i, item in enumerate(footer_list):
        brnum = re.findall(r'\d{3}-\d{2}-\d{5}', item)
        if len(brnum) == 0:
            brnum = re.findall(r'\d{10}', item)
        if len(brnum) == 0:
            footer_list[i] = 'no brnum'
        else:
            brum_list = []
            for br in brnum:
                br = br.replace('-', '')
                brum_list.append(br)
            footer_list[i] = brum_list

    print(footer_list)
    # brnum = re.findall(r'\d{3}-\d{2}-\d{5}', footer)
    # url = ""
    # if len(brnum) == 0:
    #     brnum = re.findall(r'\d{10}', footer)
    # if len(brnum) == 0:
    #     brnum = 'no brnum'
    # else:
    #     brnum = brnum[0]
    #     brnum = brnum.replace('-', '')  # '-'을 제거
    #     url = 'https://www.ftc.go.kr/bizCommPop.do?wrkr_no='+brnum
    # print(brnum)










