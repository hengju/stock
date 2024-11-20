import yfinance as yf
import pandas as pd
import os

content=yf.download('^VIX', start="2024-11-01", end="2024-11-18")
content=content.sort_index(ascending=False)
if not os.path.exists("./vix.csv"):
    content.to_csv("vix.csv", header=True, index=True, encoding='utf-8')
else:
    content.to_csv("vix.csv", header=False, index=True, mode="a", encoding='utf-8')