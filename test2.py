from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Chrome 웹 드라이버 설정
driver = webdriver.Chrome()

# 웹 페이지로 이동
url = "https://www.ftc.go.kr/www/biz/bizCommList.do?key=5375"
driver.get(url)

try:
    # 사업자 번호 입력
    search_input = driver.find_element(By.ID, "boardsearch")
    search_input.send_keys("7378602910")  # 여기에 사업자 번호를 넣으세요

    # 검색 버튼 클릭
    search_button = driver.find_element(By.CLASS_NAME, "submit")
    search_button.click()

    # 데이터 로딩을 위해 잠시 대기
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tr-hover")))

    # 결과 데이터 가져오기
    results = driver.find_elements(By.CLASS_NAME, "tr-hover")
    # driver.find_elements(By.CLASS_NAME, "tr-hover")[0].get_attribute("onclick")
    for result in results:
        print(result.text)

finally:
    # 브라우저 종료
    driver.quit()
