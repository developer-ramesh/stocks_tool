import yfinance as yf
import time
from nselib import capital_market
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import db
from decimal import Decimal
from datetime import datetime

log_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_additional_data(symbol):
    link = f'https://www.screener.in/company/{symbol}'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(link, headers=hdr)
    data = {}

    try:
        page = urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')

        # Extract quarterly data
        div_html = soup.find('div', {'id': 'quarterly-shp'})
        table_html = div_html.find('table', {'class': 'data-table'})
        rows = table_html.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1:
                category = cols[0].get_text(strip=True).replace('+', '').strip()
                last_data = cols[-1].get_text(strip=True).replace('%', '').strip()
                if ',' in last_data:
                    last_data = last_data.replace(',', '')
                data[category] = float(last_data) if last_data else 0.0

        # Extract market cap data
        div_html = soup.find('div', {'class': 'company-ratios'})
        ul_html = div_html.find('ul', {'id': 'top-ratios'})

        for li in ul_html.find_all("li"):
            name_span = li.find('span', {'class': 'name'})
            if 'Market Cap' in name_span.text:
                num_span = li.find('span', {'class': 'number'}).get_text(strip=True).replace(',', '')
                market_cap = float(num_span) if num_span else 0.0
                data['Market Cap'] = market_cap
                break

    except Exception as e:
        print(f'{log_date} EXCEPTION THROWN: UNABLE TO FETCH DATA FOR {symbol}')
        print(e)

    return data


def update_stocks():
    nifty50_list = capital_market.nifty50_equity_list()
    stock_data = []

    for index, row in nifty50_list.iterrows():
        # if(index == 1):
        #     break
        symbol = row['Symbol']
        msft = yf.Ticker(symbol.lower() + ".ns")
        info = msft.history(period="1d")
        closing_price = info['Close'].iloc[0]
        closing_price = f"{closing_price:.2f}" # Format to 2 decimal places
        
        additional_data = get_additional_data(symbol)
        print(f'{log_date} Fetched data for : {symbol}')
        
        stock_data.append({
            'Company_Name': row['Company Name'],
            'Industry': row['Industry'],
            'Symbol': symbol,
            'Price': closing_price,
            'Market_Cap': Decimal(additional_data.get('Market Cap', 0)).quantize(Decimal('0.00')),
            'Promoters_Holdings': Decimal(additional_data.get('Promoters', 0)).quantize(Decimal('0.00')),
            'DLL': Decimal(additional_data.get('DIIs', 0)).quantize(Decimal('0.00')),
            'FLL': Decimal(additional_data.get('FIIs', 0)).quantize(Decimal('0.00')),
            'Government': Decimal(additional_data.get('Government', 0)).quantize(Decimal('0.00')),
            'Public': Decimal(additional_data.get('Public', 0)).quantize(Decimal('0.00')),
            'No_of_Shares': Decimal(additional_data.get('No. of Shareholders', 0)).quantize(Decimal('0.00')),
        })

        time.sleep(5)  # Sleep for 5 seconds


print(f'{log_date} Updating stocks...')
update_stocks()
