import requests
import pyperclip
from twilio.rest import Client
# Define stock of interest as well as change threshold (in %)
interested_stock = 'MCD'
interested_company = "McDonald's"
max_change = 5
API_key = "Masked"
price_API_Parameters = {'function':'TIME_SERIES_DAILY',
                  'symbol': interested_stock,
                  'outputsize': 'compact',
                  'datatype': 'json',
                  'apikey': API_key
                  }

# 1:Get the absolute difference between yesterday stock price and stock closing price for today
stock_price_response = requests.get(url='https://www.alphavantage.co/query',params=price_API_Parameters)
stock_price_response.raise_for_status()
stock_price_json = stock_price_response.json()
stock_price_data = stock_price_json["Time Series (Daily)"]
# Get back the first two keys in the dictionary (Today and yesterday)
current_date = list(stock_price_data.keys())[0]
previous_date =list(stock_price_data.keys())[1]

current_date_close_price = float(stock_price_data[current_date]["4. close"])
previous_date_close_price = float(stock_price_data[previous_date]["4. close"])

# Calculate the percentage change for the two prices
price_difference = current_date_close_price - previous_date_close_price
percentage_change = round((price_difference/previous_date_close_price) * 100, 2)
if percentage_change >0:
    dod_change = f"🔺 {percentage_change}"
else:
    dod_change = f'🔻 {percentage_change}'

# 2: If change threshold is exceeded, use an appropriate API to fetch the top 3 news articles related to the
# company and stock
if abs(percentage_change) >= max_change:
    fetch_news = True
else:
    fetch_news = False

news_API_key = "Masked"

news_API_parameters = {'q': ("+McDonald's",'stocks'),
                       'from': previous_date,
                       'to': current_date,
                       'language': 'en',
                       'pagesize': 10,
                       'sortBy': 'relevancy',
                       'apiKey': news_API_key,
                       }

if fetch_news:
    news_response = requests.get(url="https://newsapi.org/v2/everything", params=news_API_parameters)
    news_response.raise_for_status()
    news_json = news_response.json()

# Top 3 news articles
    top_news_articles = news_json['articles'][0:3]

# 3: Use twilio API to send 3 x sms to you with the following info:
# (A): Stock Name + Yesterday close price + Today close price + % Change
# (B): Articles Header + Brief + Link x 3
account_sid = 'Masked'
auth_token = 'Masked'
if fetch_news:
    for article in top_news_articles:
        client = Client(account_sid, auth_token)

        message = client.messages.create(
        body= f"Company:{interested_company}\n\n"
              f"Price Change:{dod_change}\n\n"
              f"Title: {article['title']}\n\n"
              f"Description: {article['description']}\n\n"
              f"Read more @ {article['url']}",
        from_= 'Masked',
        to='Masked'
        )

        print(message.status)








