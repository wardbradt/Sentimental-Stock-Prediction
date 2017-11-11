from sentimental_setup import *

ticker = "NVDA"

ten_q_urls = get_sec_ten_q_urls(ticker)
ten_q_soups = get_soups(ten_q_urls)

stock_json = get_stock_json(ticker)

earnings_day_reports = []

for i in ten_q_soups:
    ten_q_info = {}
    ten_q_info["date"] = get_date(i)
    print(ten_q_info["date"])
    ten_q_info["text"] = get_text_from_filing_detail_soup(i)

    stock_info_on_date = get_stock_info_from_date(stock_json, ten_q_info["date"])
    ten_q_info["open"] = float(stock_info_on_date["1. open"])
    ten_q_info["close"] = float(stock_info_on_date["4. close"])
    earnings_day_reports.append(ten_q_info)

for i in earnings_day_reports:
    print(i)

