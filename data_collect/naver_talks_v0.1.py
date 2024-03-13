# 실시간 시가총액 100위 종목정보
def top100(df_codes):
    url = 'https://msg.soledot.com/finance/fo/sisemarketsumlist.sd'

    kospi_df = pd.read_html(url)[0][['종목명']]
    kosdaq_df = pd.read_html(url)[1][['종목명']]

    kospi_df['시장'] = 'kospi'
    kosdaq_df['시장'] = 'kosdaq'

    df2 = pd.concat([kospi_df, kosdaq_df], axis=0)

    result_df = df_codes.merge(df2, left_on='회사명', right_on='종목명', how='right')
    del result_df['회사명']

    # 거래소별 종목명:종목코드 딕셔너리 생성
    result_dict = dict()
    result_dict['kospi'] = dict(zip(result_df[result_df['시장']=='kospi']['종목명'], result_df[result_df['시장']=='kospi']['종목코드']))
    result_dict['kosdaq'] = dict(zip(result_df[result_df['시장']=='kosdaq']['종목명'], result_df[result_df['시장']=='kosdaq']['종목코드']))

    return result_dict

def naver_talks_crawling(p_args):
    # User-Agent 설정
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}

    table1 = pd.DataFrame()

    for page in tqdm(range(1, p_args['max_page']+1)):
        url = 'https://finance.naver.com/item/board.naver?code=%s&page=%s' % (p_args['code'], str(page))

        # print('연결 되었습니다.:', requests.get(url, headers=headers))
        html = requests.get(url, headers=headers).content

        # 한글 깨짐 방지 decode
        soup = BeautifulSoup(html.decode('euc-kr', 'replace'), 'html.parser')
        table = soup.find('table', {'class': 'type2'})
        tb = table.select('tbody > tr')

        tmpdf2 = pd.DataFrame()
        for i in range(2, len(tb)):
            try:
                if len(tb[i].select('td > span')) > 0:
                    date = [tb[i].select('td > span')[0].text]
                    title = [tb[i].select('td.title > a')[0]['title']]
                    links = ['https://finance.naver.com' + a['href'] for a in tb[i].select('a[href]')]
                    views = [tb[i].select('td > span')[1].text]
                    pos = [tb[i].select('td > strong')[0].text]
                    neg = [tb[i].select('td > strong')[1].text]
                    tmpdf = pd.DataFrame({'페이지': page, '날짜': date, '제목': title, '조회': views,
                                        '공감': pos, '비공감': neg, '링크': links
                    })
                    tmpdf2 = pd.concat([tmpdf2, tmpdf])
            except:
                pass

        table1 = pd.concat([table1, tmpdf2])
    table1 = table1.reset_index(drop=True)
    table1['ID'] = table1.index

    today = datetime.datetime.today().strftime('%Y%m%d')
    filename = './data/naver_talks_%s_%s.csv' % (p_args['code'], today)
    if not os.path.exists(filename):
        table1.to_csv(filename, index=None, encoding='utf-8-sig')
    else:
        table1.to_csv(filename, mode='a', index=None, encoding='utf-8-sig')

    df = pd.read_csv(filename)
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['일'] = df['날짜'].dt.day
    print(df['일'].tolist()[0])

    df_grouped = df.groupby(['일']).agg( DAY=('일', 'max'), CONTS_CNT=('ID', 'count') )
    print(df_grouped)
    filename = './data/naver_talks_count_%s_%s.csv' % (p_args['code'], today)
    if not os.path.exists(filename):
        df_grouped.to_csv(filename, index=None, encoding='utf-8-sig')
    else:
        df_grouped.to_csv(filename, mode='a', index=None, encoding='utf-8-sig')


if __name__ == '__main__':
    from bs4 import BeautifulSoup
    import requests
    import pandas as pd
    import datetime
    import os
    from tqdm import tqdm
    import warnings
    from common import *
    warnings.filterwarnings('ignore')

    # key 종목명 value 종목코드
    dict_codes = get_code()
    df_codes = pd.DataFrame({'회사명':dict_codes.keys(),
                             '종목코드':dict_codes.values()})

    # 페이지 수 입력
    print('페이지 수 입력')
    max_page = int(input())
    print('입력 받은 페이지 수: ', max_page)

    result_dict = top100(df_codes)
    kospi = result_dict['kospi']
    kosdaq = result_dict['kosdaq']
    codes = ['000660']

    #<--------------------------- 나중에 DB화----------------------->#
    #<--------------------------- 나중에 기업명 매칭 확장----------------------->#
    #<--------------------------- try~except 부분 수정하기----------------------->#

    dict_args = dict()
    dict_args['max_page']=max_page

    for code in tqdm(codes):
        dict_args['code'] = code
        print('-'*120)
        print('해당 종목: ', code)

        naver_talks_crawling(dict_args)