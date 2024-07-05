from flask import Flask, jsonify, render_template
import db

app = Flask(__name__)

@app.route('/')
def home():
    stocks = db.get_all_stocks()
    news = db.get_all_news()
    return render_template('index.html', stocks=stocks, news=news, current_page='home')

@app.route('/bulkdeals')
def bulkdeals():
    bulkdeals = db.get_all_bulkdeals()
    results = db.get_quarterly_results()
    return render_template('bulkdeals.html', bulkdeals=bulkdeals, results=results, current_page='bulkdeals')


if __name__ == '__main__':
     app.run(host='0.0.0.0', port=8000, debug=True)
