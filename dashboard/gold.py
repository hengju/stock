import pandas as pd
import os

nums=list(range(1,11))
for num in nums:
    url="https://finance.naver.com/marketindex/worldDailyQuote.naver?marketindexCd=CMDT_GC&fdtc=2&page=%d" %num
    print(url)
    content=pd.read_html(url)[0]
    if not os.path.exists("./gold.csv"):
        content.to_csv("gold.csv", header=True, index=False, encoding='euc-kr')
    else:
        content.to_csv("gold.csv", header=False, index=False, mode="a", encoding='euc-kr')