from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
from textblob import TextBlob

# gets the urls of the filing details for the past 100 10-Q reports
def get_sec_ten_q_urls(ticker):
    r = requests.get("https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="+ticker+"&type=10-Q&dateb=&owner=exclude&count=100")
    soup = BeautifulSoup(r.text, "html.parser")

    table_of_ten_q = soup.find_all("table", class_="tableFile2")[0]
    # the first row is the header: does not have data we want, so get all rows after index 1
    ten_q_table_rows = table_of_ten_q.find_all("tr")[1:]
    urls = []
    for i in ten_q_table_rows:
        urls.append("https://www.sec.gov" + i.find_all("td")[1].a.get("href"))
    return urls


# creates the beautiful soup objects for a given set of URLs
def get_soups(urls):
    soups = []
    for i in urls:
        td_request = requests.get(i)
        soups.append(BeautifulSoup(td_request.text, "html.parser"))
    return soups


# gets the date on which the 10-Q was filed
def get_date(ten_q_filing_detail_soup):
    return ten_q_filing_detail_soup.find_all("div", class_="info")[0].get_text()


# Takes a str and returns the index of the first occurence of 'Overview' after 'MANAGEMENT’S'
def findOverviewStr(text):
    try:
        ITEM_2_index = text.index('MANAGEMENT’S')
    except:
        print(text)
    return text[text[ITEM_2_index:].index('Overview') + ITEM_2_index:]


# gets the text of the 10-Q report from its filing detail page
def get_text_from_filing_detail_soup(ten_q_filing_detail_soup):
    # the <tr> with the html document we want.
    tableRow = ten_q_filing_detail_soup.table.find_all('tr')[1]
    # request the quarterly earnings report.
    req = requests.get("https://www.sec.gov/" + tableRow.find_all('td')[2].a.get('href'))

    fileSoup = BeautifulSoup(req.text, "html.parser")
    return findOverviewStr(fileSoup.get_text())


def get_stock_json(ticker):
    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY'
    url += '&symbol=' + ticker
    url += '&apikey=' + '6XY1XB60WTW1JD6G'
    return requests.get(url).json()


# date must be of the form "YYYY-MM-DD"
def get_stock_info_from_date(stock_json, date):
    formatted_date = datetime.strptime(date, "%Y-%m-%d")
    while datetime.strftime(formatted_date, "%Y-%m-%d") not in stock_json["Time Series (Daily)"]:
        formatted_date += timedelta(days=1)
    return stock_json["Time Series (Daily)"][datetime.strftime(formatted_date, "%Y-%m-%d")]

nvda_json = get_stock_json("NVDA")
get_stock_info_from_date(nvda_json, "2017-06-24")
# blob = TextBlob(text)
# x = 0.0
# i = 0
# for sentence in blob.sentences:
#     x += sentence.sentiment.polarity
#     i += 1
#
#
# print(x/i)
