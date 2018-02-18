# Sentimental Stock Prediction

## Example Usage

Firstly, you must set `quandl.ApiConfig.api_key` at the top of sentimental.py to your quandl API key. 

You can get a key [here](https://www.quandl.com/tools/api).
```
from sentimental import generate_earnings_day_reports

# can be any stock ticker
ticker = "NVDA"
generate_earnings_day_reports(ticker)
```
Now when you view index.html, you will be able to view the visualization for your ticker.
## To Do:
- Find a better way to find the discussion/ overview section of each report than the current implementation in `find_overview_str`
- Fix price axis scaling
