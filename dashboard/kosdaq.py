# 코스닥
import pandas as pd
import os

nums=list(range(1,11))
for num in nums:
    url="https://finance.naver.com/sise/sise_index_day.naver?code=KOSDAQ&page=%d" %num
    print(url)
    content=pd.read_html(url)[0]
    content=content.dropna()
    if not os.path.exists("./kosdaq.csv"):
        content.to_csv("kosdaq.csv", header=True, index=False, encoding='euc-kr')
    else:
        content.to_csv("kosdaq.csv", header=False, index=False, mode="a", encoding='euc-kr')