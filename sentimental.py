from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime, timedelta
from textblob import TextBlob
import quandl

# note: you must get your own API key to use this code.
quandl.ApiConfig.api_key = 'your_api_key'


# gets the urls of the filing details for the past 100 10-Q reports
def get_sec_ten_q_urls(ticker: str, amount=100):
    """
    :param ticker: A stock ticker
    :param amount: How many urls the method retrieves
    :return: the urls for the past amount (default 100) ticker 10-Q report Filing Details.
    """
    r = requests.get(
        "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=10-Q&dateb=&owner=exclude&count="
        "{}".format(ticker, str(amount)))
    soup = BeautifulSoup(r.text)

    ten_q_table = soup.find_all("table", class_="tableFile2")[0]
    # the first row is the header: does not have data we want, so get all rows after index 1
    ten_q_table_rows = ten_q_table.find_all("tr")[1:]
    urls = []
    for i in ten_q_table_rows:
        urls.append("https://www.sec.gov" + i.find_all("td")[1].a.get("href"))
    return urls


def get_soups(urls: list):
    """
    Creates a list of Beautiful Soup objects (one created for the text of each url in urls, a list of URLs)
    """
    soups = []
    for i in urls:
        td_request = requests.get(i)
        soups.append(BeautifulSoup(td_request.text, "html.parser"))
    return soups


def get_date(ten_q_filing_detail_soup):
    """
    Given a Beautiful Soup object representing a Filing Detail Page, return on what data the 10-Q was filed.
    """
    return ten_q_filing_detail_soup.find_all("div", class_="info")[0].get_text()


def find_overview_str(text):
    """
    Returns the index of the first occurrence of 'Overview' after 'MANAGEMENT’S' in text
    """
    ITEM_2_index = text.index('MANAGEMENT’S')
    return text[text[ITEM_2_index:].index('Overview') + ITEM_2_index:]


def get_text_from_filing_detail_soup(ten_q_filing_detail_soup: BeautifulSoup):
    """
    Returns the text of the 10-Q report from its Filing Detail page
    """
    # the <tr> with the html document we want.
    table_row = ten_q_filing_detail_soup.table.find_all('tr')[1]
    # request the quarterly earnings report.
    req = requests.get("https://www.sec.gov/{}".format(str(table_row.find_all('td')[2].a.get('href'))))

    file_soup = BeautifulSoup(req.text, "html.parser")
    return file_soup.get_text()


def get_text_sentiment(text: str):
    """
    Given a piece of text, returns the average sentiment polarity of its sentences
    """
    blob = TextBlob(text)
    count = 0
    total = 0.0
    for sentence in blob.sentences:
        total += sentence.sentiment.polarity
        count += 1
    return total / count


def get_nearest_date(date, stock_df):
    """
    Given a date in the format YYYY-MM-DD, returns the date closest to data in stock_df larger than date
    """
    formatted_date = datetime.strptime(date, "%Y-%m-%d")
    while datetime.strftime(formatted_date, "%Y-%m-%d") not in stock_df.index:
        formatted_date += timedelta(days=1)
    return datetime.strftime(formatted_date, "%Y-%m-%d")


def write_stock_history_json(stock_dataframe, ticker):
    """
    Given a data frame representing a stock's history, writes that DF to a file named ticker+"_history".json
    :param stock_dataframe:
    :param ticker:
    """
    array_of_dicts = stock_dataframe.reset_index().to_dict('records')

    for i in range(len(array_of_dicts)):
        date = str(array_of_dicts[i]["date"])
        date = date[:date.index(" ")]
        array_of_dicts[i]["date"] = date
    with open('{}_history.json'.format(ticker), 'w') as outfile:
        json.dump(array_of_dicts, outfile)


# does all of the real work: writing to json, getting historical stock info data frame.
# pretty much uses other functions as auxiliaries
# returns a tuple of the historical stock info data frame and the earnings day reports
def generate_earnings_day_reports(ticker):
    ten_q_urls = get_sec_ten_q_urls(ticker)
    ten_q_soups = get_soups(ten_q_urls)

    earnings_day_reports = []

    max_date = ""
    min_date = ""
    for soup in ten_q_soups:
        ten_q_info = {"date": get_date(soup)}

        if max_date == "":
            max_date = ten_q_info["date"]
        min_date = ten_q_info["date"]

        ten_q_info["sentiment"] = get_text_sentiment(get_text_from_filing_detail_soup(soup))

        earnings_day_reports.append(ten_q_info)

    stock_data = quandl.get_table('WIKI/PRICES', qopts={'columns': ['date', 'open', 'close']}, ticker=[ticker],
                                  date={'gte': min_date, 'lte': max_date})
    stock_data = stock_data.set_index("date")
    for report in earnings_day_reports:
        date = report["date"]
        date = get_nearest_date(date, stock_data)

        report["open"] = float(stock_data.loc[date, "open"])
        report["close"] = float(stock_data.loc[date, "close"])

    with open(ticker + '_info.json', 'w') as outfile:
        json.dump(earnings_day_reports, outfile)

    write_stock_history_json(stock_data, ticker)
