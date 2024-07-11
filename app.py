from flask import Flask, jsonify, render_template
import db
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    stocks = db.get_all_stocks()
    news = db.get_all_news()
    
    formatted_stocks = []
    for stock in stocks:
        stock_list = list(stock)
        if isinstance(stock_list[8], datetime):
            stock_list[8] = stock_list[8].strftime('%d %B %Y, %I:%M %p')
        formatted_stocks.append(tuple(stock_list))
    
    last_updated = news[0][4].strftime('%d %B %Y, %I:%M %p')
    return render_template('index.html', stocks=formatted_stocks, news=news, last_updated=last_updated, current_page='home')

@app.route('/bulkdeals')
def bulkdeals():
    bulkdeals = db.get_all_bulkdeals()
    results = db.get_quarterly_results()
    return render_template('bulkdeals.html', bulkdeals=bulkdeals, results=results, current_page='bulkdeals')


if __name__ == '__main__':
     app.run(host='0.0.0.0', port=8000, debug=True)
