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

def crawling(p_args):
    driver = connect_chrome()
    p_args['base_url']='https://finance.daum.net/quotes/A%s#news/stock' %(p_args['code'])
    driver.get(p_args['base_url'])
    time.sleep(5)

    result_df = pd.DataFrame()
    for page in range(1,p_args['max_page']+1):
        print('현재 페이지: ', page)
        # 사이트 하단 페이지 버튼 클릭해서 페이지 넘기기
        if page >= 2:
            if page % 10 == 1:
                driver.execute_script(
                    '''
                    document.querySelector("#boxContents a.btnNext").click();
                    ''')

            else:
                page_xpath = f'''//*[@class="btnMove" and text()={page}]'''
                x = driver.find_element(By.XPATH, page_xpath)
                driver.execute_script("arguments[0].click();", x)

        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        temp_list = list()
        for i in soup.select('#boxContents .tit'):
            date = i.find_next_sibling("p").text.split(' · ')[1]
            title = i.text
            link = p_args['base_url'] + '/' + i['href'].split('/')[-1]
            source = i.find_next_sibling("p").text.split(' · ')[0]

            temp_list.append({
                'date': date,
                'title': title,
                'link': link,
                'source': source
            })

        temp_df = pd.DataFrame(temp_list)
        # print(temp_df)
        result_df = pd.concat([result_df, temp_df])
    time.sleep(3)
    result_df = result_df.reset_index(drop=True)
    result_df = result_df[(result_df['date']>=p_args['initial_dates'][0])&(result_df['date']<=p_args['initial_dates'][1])]    # 오늘 뉴스만 확인
    # result_df = result_df[result_df['date'] == today]    # 오늘 뉴스만 확인

    if not os.path.exists(f'./data/daum_news_links_{code}.csv'):
        result_df.to_csv(f'./data/daum_news_links_{code}.csv', index=None, encoding='utf-8-sig')
    else:
        result_df.to_csv(f'./data/daum_news_links_{code}.csv', mode='a', index=None, encoding='utf-8-sig')

    driver.quit()


if __name__ == '__main__':
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from bs4 import BeautifulSoup
    import pandas as pd
    import time
    import os
    from tqdm import tqdm
    import warnings
    from common import *
    warnings.filterwarnings('ignore')

    # key 종목명 value 종목코드
    dict_codes = get_code()

    # 해당 종목명 혹은 종목코드 입력
    print('종목명 혹은 종목코드 입력')
    input_codes = list(input().split())
    # print('입력 받은 코드: ', input_codes)
    codes = [dict_codes.get(code) if not code.isdigit() else code for code in input_codes]
    codes = list(set(codes))
    print(codes)

    # 날짜 입력 (%Y.%m.%d) (%Y.%m.%d)
    print('수집 데이터에 해당하는 시작 날짜와 종료 날짜 입력 (%Y.%m.%d) (%Y.%m.%d)')
    initial_dates = list(input().split())
    print('입력 받은 날짜: ', initial_dates)

    # 페이지 수 입력
    print('페이지 수 입력')
    max_page = int(input())
    print('입력 받은 페이지 수: ', max_page)

    #<--------------------------- 나중에 DB화----------------------->#
    #<--------------------------- 나중에 기업명 매칭 확장----------------------->#

    dict_args = dict()
    dict_args['initial_dates']=initial_dates
    dict_args['max_page']=max_page

    for code in tqdm(codes):
        dict_args['code'] = code
        print('-'*120)
        print('해당 종목: ', code)

        crawling(dict_args)