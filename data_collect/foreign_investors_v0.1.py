def line_logging(*messages):
    import datetime
    log_time = (datetime.datetime.today() + datetime.timedelta(hours=9)).strftime('[%Y/%m/%d %H:%M:%S]')    # 한국시간(UTC+9hrs)
    log = list()
    for message in messages:
        log.append(str(message))
    print(log_time + ':[' + ' '.join(log) + ']', flush=True)

# 5일 기간 내 외국인 순매수/순매도 상위 종목 데이터 받기
def save_investors_info(driver):

    driver.get(url_list["influential_investors"])

    time.sleep(2)
    path_xpath = '''//*[@id="boxInfluentialInvestors"]/div[1]/div/select/option[2]'''
    driver.find_element(By.XPATH, path_xpath).click()
    time.sleep(2)

    html = driver.page_source
    soup = bs(html)
    results = pd.read_html(html)[1]
    results.head()

    time.sleep(1)
    driver.quit()

    # 순매수, 순매도 리스트 2개 생성
    buy_df = results[[('순매수 종목',   '종목명'),('순매수 종목',  '금액 -'),('순매수 종목',  '수량 -'),('순매수 종목', '등락률 -')]]
    sell_df = results[[('순매도 종목',   '종목명'),('순매도 종목',  '금액 -'),('순매도 종목',  '수량 -'),('순매도 종목', '등락률 -')]]

    buy_df.columns = [1,2,3,4]
    sell_df.columns = [1,2,3,4]

    column_names = {1:'종목명',2:'금액',3:'수량',4:'등락률'}

    buy_df = buy_df.rename(columns=column_names)
    sell_df = sell_df.rename(columns=column_names)

    company_df = pd.read_excel('상장법인목록.xlsx', usecols=['회사명','종목코드','업종','주요제품'], header=0)
    company_df = company_df.rename(columns={"회사명": "종목명"})

    buy_df = buy_df.merge(company_df[company_df['종목명'].isin(buy_df['종목명'].tolist())], on="종목명", how="left")
    sell_df = sell_df.merge(company_df[company_df['종목명'].isin(sell_df['종목명'].tolist())], on="종목명", how="left")

    buy_df.to_csv(os.path.join(outputPath, '5days_foreign_buy.csv'), index=None, encoding='utf-8')
    sell_df.to_csv(os.path.join(outputPath, '5days_foreign_sell.csv'), index=None, encoding='utf-8')

    time.sleep(3)
    driver.quit()

def connect_chrome():
    options = ChromeOptions()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    options.add_argument('user-agent=' + user_agent)
    options.add_argument("lang=ko_KR")
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument("--no-sandbox")

    # 크롬 드라이버 최신 버전 설정
    service = ChromeService(executable_path=ChromeDriverManager().install())

    # chrome driver
    driver = webdriver.Chrome(service=service, options=options) # <- options로 변경
    driver.implicitly_wait(60) # 웹자원 로드를 위해 대기

    return driver


if __name__ == '__main__':
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from bs4 import BeautifulSoup as bs
    import requests
    import pandas as pd
    import time
    import os
    import warnings

    #====================================================================================================================
    # SETTING
    #--------------------------------------------------------------------------------------------------------------------

    # 빈 폴더 생성
    # if not os.path.exists('input'):
    #     os.mkdir('input')
    if not os.path.exists('output'):
        os.mkdir('output')

    # PATH 지정
    rootPath = os.getcwd()

    # inputPath = os.path.join(rootPath, 'input')
    outputPath = os.path.join(rootPath, 'output')

    # 경고 메시지 무시
    warnings.filterwarnings('ignore')

    # URL 설정
    url_list = {  "influential_investors":"https://finance.daum.net/domestic/influential_investors?market=KOSPI"
                # , "foreign_shares":"https://finance.daum.net/domestic/foreign_shares?market=KOSPI"
               }
    #====================================================================================================================

    # 함수 실행
    driver = connect_chrome()
    line_logging('첫번째 프로세스 시작합니다.')
    save_investors_info(driver)
    line_logging('첫번째 프로세스 종료합니다.')