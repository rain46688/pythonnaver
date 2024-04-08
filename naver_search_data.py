import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re

def get_data(keyword):

    # 아이템을 담을 배열 선언
    ad_items = []

    # 첫번째 페이지 가져온 후 증가하면서 가져오기
    index = 1
    while True:
        # 네이버 파워링크 검색결과 가져오기
        url = f'https://ad.search.naver.com/search.naver?where=ad&query={
            keyword}&pagingIndex={index}'
        # 헤더 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107 Safari/537.36'
        }
        # 요청 보내기
        response = requests.get(url, headers=headers)
        # 파싱하기
        soup = BeautifulSoup(response.text, 'html.parser')
        # 검색결과가 없을 경우 종료
        if ('검색결과가 없습니다.' in soup.text):
            if index == 1:
                print("검색결과가 없습니다.")
            break
        # 인덱스 증가
        index += 1
        # 아이템 추가
        ad_items.extend(soup.find_all('li', class_='lst'))

    # 결과를 담을 배열 선언
    ads_info = []

    # 아이템을 하나씩 가져와서 데이터 파싱
    for ad_item in ad_items:
        # 데이터가 아닌건 제외
        if ad_item.contents.__len__() < 2:
            continue

        # URL 영역 데이터 파싱
        url_data = ""
        url_data2= ""
        # URL 영역 데이터가 있을 경우 파싱
        if (ad_item.find('div', class_='url_area') != None):
            udata = ad_item.find('div', class_='url_area').text
            url_data = [item.strip()
                        for item in (udata).split('\n') if item.strip()]
            url_data2 = ad_item.find('a', class_='url').get('href')

        # TIT_WRAP 데이터 파싱
        tit_wrap_data = ""
        # TIT_WRAP 데이터가 있을 경우 파싱
        if (ad_item.find('a', class_='tit_wrap') != None):
            tdata = ad_item.find('a', class_='tit_wrap').text
            tit_wrap_data = [item.strip()
                             for item in (tdata).split('\n') if item.strip()]

        # DESC 영역 데이터 파싱
        desc_data = ""
        # DESC 영역 데이터가 있을 경우 파싱
        if (ad_item.find('div', class_='desc_area') != None):
            ddata = ad_item.find('div', class_='desc_area').text
            desc_data = [item.strip()
                         for item in (ddata).split('\n') if item.strip()]

         # 광고 데이터 제외
        keywords = ['blog.naver', 'smartstore.naver.', 'lotteon',
                    'gsshop', 'gmarket', 'cjonstyle', '11st', 'yes24', 'coupang', 'auction', 'youtube', 'yadoc','숨고','cafe.naver',
                    'temu','navimro' ,'ssg' ,'ohou','place.naver','선거의신' , '기프트한국', 'soomgo','kmong' ,'tmon', '엠알오','롯데','다나와','쇼핑','GSSHOP','toolsmro']
        contains_keyword = any(
            key_item in url_data[0] for key_item in keywords)
        if (contains_keyword):
            continue
        
        # 풋터 데이터 가져오기
        footer = get_footer(url_data2)
        brnum = re.findall(r'\d{3}-\d{2}-\d{5}', footer)
        url = ""
        if len(brnum) == 0:
            brnum = re.findall(r'\d{10}', footer)
        if len(brnum) == 0:
            brnum = 'no brnum'
        else:
            brum_list = []
            for br in brnum:
                br = br.replace('-', '')
                brum_list.append(br)
            brnum = brum_list

        # 사업자 등록 번호로 사업자 정보 조회    
        result = business_info(brnum)
        
        # 데이터 추가
        ads_info.append({
            "URL": url_data2,
            "법인명": result['bzmnNm'] if result != "no_business_data" else 'N/A',
            "사업자번호": result['brno'] if result != "no_business_data" else brnum,
            "주소": result['lctnRnAddr'] if result != "no_business_data" else 'N/A',
            "대표자명": result['rprsvNm'] if result != "no_business_data" else 'N/A',
            "법인여부": result['corpYnNm'] if result != "no_business_data" else 'N/A',
            "우편번호": result['lctnRnOzip'] if result != "no_business_data" else 'N/A',
            "도메인명": result['domnCn'] if result != "no_business_data" else 'N/A',
            "전화번호": result['telno'] if result != "no_business_data" else 'N/A',
            "타이틀 데이터": tit_wrap_data,
            "주석 데이터": desc_data,
            "URL 관련 데이터": url_data[0],
        })

    # 결과 반환
    return ads_info

# 사업자 등록 번호로 사업자 정보 조회
def business_info(brnum_list):
    try:
        for index, brnum in enumerate(brnum_list):
            url = f'http://apis.data.go.kr/1130000/MllBsDtl_1Service/getMllBsInfoDetail_1?serviceKey=WnSxz8IYNPKD1GHWGrbiTrwza%2BLcTvpWYdnr%2Famh6shKS07Aby1pHf7LPZd7TcDRPFHg%2FcfTFEkuECPIeivhmw%3D%3D&pageNo=1&numOfRows=10&resultType=json&brno={brnum}'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            items = data['items']

            if brnum_list == 'no brnum' or (len(brnum_list) - 1 == index and len(items) == 0) or len(brnum_list) > 5:
                return "no_business_data"
            
            if len(items) == 0:
                continue
            
            info_data = {
                'bzmnNm' : items[0]['bzmnNm'],
                'brno' : items[0]['brno'],
                'lctnRnAddr' : items[0]['lctnRnAddr'],
                'rprsvNm' : items[0]['rprsvNm'],
                'corpYnNm' : items[0]['corpYnNm'],
                'lctnRnOzip' : items[0]['lctnRnOzip'],
                'domnCn' : items[0]['domnCn'],
                'telno' : items[0]['telno'],
            }
            return info_data
    except Exception as e:
        print(e)
        return "no_business_data"

# 엑셀로 내보내기
def expoert_excel(data):
    df = pd.DataFrame(data)
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    df.to_excel(f'{keyword}_excel_{now}.xlsx', index=False)
    print("가져오기 완료")

# 풋터 가져오기
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

        # 풋터 검색
        if soup.find('footer') != None:
            footer_text = soup.find('footer').get_text()
        elif soup.find('div', class_='footer') != None:
            footer_text = soup.find('div', class_='footer').get_text()
        elif soup.find('div', id='footer') != None:
            footer_text = soup.find('div', id='footer').get_text()
        else:
            footer_text = soup.get_text()
            # 추가 로직
            find_all_tags = soup.find_all(lambda tag: tag.name != 'script' and ('번호' in tag.text or '사업' in tag.text))

            for tag in find_all_tags:
                tag_string = str(tag)
                footer_text += tag_string

        return footer_text
    except Exception as e:
        print(f"error2 : {e}")
    return 'no footer'

# HTML 가져오기
def get_html(url):
    try:
        # 웹 드라이버 설정
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        
        # 웹 페이지 가져오기
        driver.get(url)
        
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'footer')))
        
        # 페이지 소스 가져오기
        html_content = driver.page_source
        
        # driver.quit()
        
        return html_content
    except Exception as e:
        print(f"get_html error : {e}")
        return None    

# 메인 함수
if __name__ == "__main__":
    # 검색어 입력
    keyword = input("키워드 입력 : ")
    ads_info = get_data(keyword)
    print(f'{ads_info.__len__()} 개')
    if (ads_info.__len__() != 0):
        expoert_excel(ads_info)
