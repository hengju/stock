def get_code(file='상장법인목록.xlsx'):
    # 코스피/코스닥 상장 종목코드 읽기
    import pandas
    df = pandas.read_excel(file, usecols=['회사명','종목코드'], dtype={'회사명':str, '종목코드':str})
    dict_codes = dict(zip(df['회사명'],df['종목코드']))
    return dict_codes
    # print(dict_codes)
    # print('코스피 상장 시가총액 1위 종목: ', dict_codes.get('005930'))