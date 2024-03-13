import requests
from bs4 import BeautifulSoup as bs
import time
from multiprocessing import Pool # Pool import하기
import multiprocessing as mp
import pandas as pd
from tqdm import tqdm
from common import *
import warnings
warnings.filterwarnings('ignore')

def chromedriver_setup():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from webdriver_manager.chrome import ChromeDriverManager

    options = ChromeOptions()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
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

    return driver

def get_links(code):
    df = pd.read_csv(f'./data/daum_news_links_{code}.csv')[:10]  # 10개만 테스트
    df['idx'] = df.index
    data = list(zip(df['idx'], df['link']))
    return data

def get_content(link):

    # c_proc = mp.current_process()
    # print("Running on Process",c_proc.name,"PID",c_proc.pid)
    # time.sleep(1)
    # print("Ended",link,"Process",c_proc.name)

    driver = chromedriver_setup()
    driver.get(link[1])
    time.sleep(1)
    html = driver.page_source
    soup = bs(html, 'html.parser')
    idx = link[0]
    content = ' '.join([i.text for i in soup.select('#dmcfContents')])

    result = str(idx) + '|' + content
    print(result[:20])

    time.sleep(1)
    driver.quit()
    return result


if __name__=='__main__':

    # key 종목명 value 종목코드
    dict_codes = get_code()

    # 해당 종목명 혹은 종목코드 입력
    print('종목명 혹은 종목코드 입력')
    input_codes = list(input().split())
    # print('입력 받은 코드: ', input_codes)
    codes = [dict_codes.get(code) if not code.isdigit() else code for code in input_codes]
    codes = list(set(codes))
    print(codes)

    start_time = time.time()
    pool = Pool(processes=2)

    # 한번에 뉴스 사이트 2개 열어서 병렬로 기사내용 가져오기
    for code in tqdm(codes):
        result = pool.map(get_content, get_links(code)) # get_content 함수를 넣어주기

        new_df = pd.DataFrame({'result': result})
        print(new_df)
        new_df.to_csv(f'./data/daum_news_contents_{code}.csv', index=None, encoding='utf-8-sig')

    print("--- %s seconds ---" % (time.time() - start_time))

    time.sleep(5)
    pool.terminate()
    pool.join()