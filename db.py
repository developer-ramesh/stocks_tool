import mysql.connector
from datetime import datetime
from decimal import Decimal

log_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Database connection setup
def connect_db():
    # Remote connection for live server
    # https://console.aiven.io/account/a4c404e24e9b/admin/organization/overview
    return mysql.connector.connect(
        host='mysql-d1ae753-rameshcq.e.aivencloud.com',
        user='avnadmin',
        password='AVNS_j-4KPNmUlbKlY3Yq7Sg',
        database='capsqelq_stocks',
        port=24744,
        ssl_ca='ca.pem'
    )
    
    # # Localhost connection
    # return mysql.connector.connect(
    #     host='localhost',
    #     user='root',
    #     password='password',
    #     database='stocks'
    # )

def get_all_stocks():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT company_name, symbol, promoters_holdings, fll, dll, government, public, no_of_shares, last_updated FROM nifty50_stocks WHERE is_visible=true ORDER BY last_updated DESC;")
    stocks = cur.fetchall()
    cur.close()
    conn.close()
    return stocks

def get_all_news():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM news ORDER BY description DESC LIMIT 50;")
    news = cur.fetchall()
    cur.close()
    conn.close()
    return news

def get_all_bulkdeals():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT symbol, company_name, clientName, buySell, qty, watp, remarks FROM bulkdeals")
    bulkdeals = cur.fetchall()
    cur.close()
    conn.close()
    return bulkdeals

def get_quarterly_results():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT symbol, company_name, broadCastDate FROM quarterly_results ORDER BY last_updated DESC;")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def calculate_percentage(val_1, val_2):
    if val_1 is not None and val_2 is not None:
        if val_1 != val_2:
            difference = val_1 - val_2
            percentage_difference = (difference / val_2) * 100
            return percentage_difference
    return None

def get_events():
    conn = connect_db()
    cur = conn.cursor()
    query = """
    SELECT symbol, company_name, purpose, broadCastDate
    FROM events
    WHERE broadCastDate > CURDATE()
    ORDER BY broadCastDate ASC;
    """
    cur.execute(query)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results
