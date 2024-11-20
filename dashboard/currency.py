# 환율(달러대원화)
import pandas as pd
import os

nums=list(range(1,11))
for num in nums:
    url="https://finance.naver.com/marketindex/exchangeDailyQuote.naver?marketindexCd=FX_USDKRW&page=%d" %num
    print(url)
    content=pd.read_html(url)[0]
    if not os.path.exists("./currency.csv"):
        content.to_csv("currency.csv", header=True, index=False, encoding='euc-kr')
    else:
        content.to_csv("currency.csv", header=False, index=False, mode="a", encoding='euc-kr')