import mysql.connector
from datetime import datetime
from decimal import Decimal
from mail_sender import send_email

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

def create_table():
    conn = connect_db()
    cur = conn.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS nifty50_stocks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        company_name VARCHAR(255),
        industry VARCHAR(255),
        symbol VARCHAR(255) UNIQUE,
        price DECIMAL(20, 2),
        market_cap DECIMAL(20, 2),
        promoters_holdings DECIMAL(5, 2),
        dll DECIMAL(5, 2),
        fll DECIMAL(5, 2),
        government DECIMAL(5, 2),
        public DECIMAL(5, 2),
        no_of_shares DECIMAL(20, 2),
        is_visible BOOLEAN DEFAULT FALSE,
        created_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP
    );
    '''
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()

def create_news_table():
    conn = connect_db()
    cur = conn.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS news (
        id INT AUTO_INCREMENT PRIMARY KEY,
        stock_id INT,
        heading VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        created_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(stock_id) REFERENCES nifty50_stocks(id)
    );
    '''
    cur.execute(create_table_query)
    conn.commit()
    cur.close()
    conn.close()

def insert_stock_data(stock_data):
    conn = connect_db()
    cur = conn.cursor()

    fetch_query = '''
    SELECT id, market_cap, promoters_holdings, dll, fll, government, public, no_of_shares
    FROM nifty50_stocks
    WHERE symbol = %s;
    '''

    insert_query = '''
    INSERT INTO nifty50_stocks (
        company_name, industry, symbol, price, market_cap, promoters_holdings,
        dll, fll, government, public, no_of_shares, created_dt, last_updated, is_visible
    ) VALUES (
        %(Company_Name)s, %(Industry)s, %(Symbol)s, %(Price)s, %(Market_Cap)s,
        %(Promoters_Holdings)s, %(DLL)s, %(FLL)s, %(Government)s, %(Public)s, %(No_of_Shares)s, %(Date)s, %(Last_Updated)s, %(is_visible)s
    )
    ON DUPLICATE KEY UPDATE
        price = VALUES(price),
        market_cap = VALUES(market_cap),
        promoters_holdings = VALUES(promoters_holdings),
        dll = VALUES(dll),
        fll = VALUES(fll),
        government = VALUES(government),
        public = VALUES(public),
        no_of_shares = VALUES(no_of_shares),
        last_updated = VALUES(last_updated),
        is_visible = VALUES(is_visible);
    '''

    news_insert_query = '''
    INSERT INTO news (stock_id, heading, description, created_dt)
    VALUES (%s, %s, %s, %s);
    '''

    delete_news = cur.execute("DELETE from news;")
    print(f'{log_date} Deleted all news')

    inserted_records_count = 0
    updated_records_count = 0

    for stock in stock_data:
        stock['Date'] = datetime.now()
        stock['Last_Updated'] = datetime.now()

        cur.execute(fetch_query, (stock['Symbol'],))
        existing_data = cur.fetchone()

        if existing_data:
            stock_id, existing_market_cap, existing_promoters_holdings, existing_dll, existing_fll, existing_government, existing_public, existing_no_of_shares = existing_data
            
            message_parts = []
            is_visible = False

            if stock['Market_Cap'] is not None and existing_market_cap is not None:
                if stock['Market_Cap'] != existing_market_cap:
                    if stock['Market_Cap'] < existing_market_cap:
                        message_parts.append(f"Market Cap value <span class='bear'>decreased</span>, Prev: {existing_market_cap:.0f} Last: {stock['Market_Cap']:.0f}")
                    else:
                        message_parts.append(f"Market Cap value <span class='bull'>increased</span>, Prev: {existing_market_cap:.0f} Last: {stock['Market_Cap']:.0f}")
                        is_visible = True

            if stock['Promoters_Holdings'] is not None and existing_promoters_holdings is not None:
                if stock['Promoters_Holdings'] != existing_promoters_holdings:
                    if stock['Promoters_Holdings'] < existing_promoters_holdings:
                        message_parts.append("Promoters holdings <span class='bear'>decreased</span>, Prev: " + str(existing_promoters_holdings) + " Last: " + str(stock['Promoters_Holdings']))
                    else:
                        message_parts.append("Promoters holdings <span class='bull'>increased</span>, Prev: " + str(existing_promoters_holdings) + " Last: " + str(stock['Promoters_Holdings']))
                        is_visible = True

            if stock['DLL'] is not None and existing_dll is not None:
                if stock['DLL'] != existing_dll:
                    if stock['DLL'] < existing_dll:
                        message_parts.append("DLL holding <span class='bear'>decreased</span>, Prev: " + str(existing_dll) + " Last: " + str(stock['DLL']))
                    else:
                        message_parts.append("DLL holding <span class='bull'>increased</span>, Prev: " + str(existing_dll) + " Last: " + str(stock['DLL']))
                        is_visible = True

            if stock['FLL'] is not None and existing_fll is not None:
                if stock['FLL'] != existing_fll:
                    if stock['FLL'] < existing_fll:
                        message_parts.append("FLL holding <span class='bear'>decreased</span>, Prev: " + str(existing_fll) + " Last: " + str(stock['FLL']))
                    else:
                        message_parts.append("FLL holding <span class='bull'>increased</span>, Prev: " + str(existing_fll) + " Last: " + str(stock['FLL']))
                        is_visible = True

            if stock['Government'] is not None and existing_government is not None:
                if stock['Government'] != existing_government:
                    if stock['Government'] < existing_government:
                        message_parts.append("Government holding <span class='bear'>decreased</span>, Prev: " + str(existing_government) + " Last: " + str(stock['Government']))
                    else:
                        message_parts.append("Government holding <span class='bull'>increased</span>, Prev: " + str(existing_government) + " Last: " + str(stock['Government']))
                        is_visible = True

            if stock['Public'] is not None and existing_public is not None:
                if stock['Public'] != existing_public:
                    if stock['Public'] < existing_public:
                        message_parts.append("Public holding <span class='bear'>decreased</span>, Prev: " + str(existing_public) + " Last: " + str(stock['Public']))
                    else:
                        message_parts.append("Public holding <span class='bull'>increased</span>, Prev: " + str(existing_public) + " Last: " + str(stock['Public']))
                        is_visible = True

            if stock['No_of_Shares'] is not None and existing_no_of_shares is not None:
                if stock['No_of_Shares'] != existing_no_of_shares:
                    if stock['No_of_Shares'] < existing_no_of_shares:
                        message_parts.append("No of Shareholders <span class='bear'>decreased</span>, Prev: " + str(existing_no_of_shares) + " Last: " + str(stock['No_of_Shares']))
                    else:
                        message_parts.append("No of Shareholders <span class='bull'>increased</span>, Prev: " + str(existing_no_of_shares) + " Last: " + str(stock['No_of_Shares']))
                        is_visible = True

            if message_parts:
                updated_records_count += 1
                heading = f"Alert for {stock['Symbol']}"
                description = "\n ".join(message_parts)
                created_dt = datetime.now()
                cur.execute(news_insert_query, (stock_id, heading, description, created_dt))
                print(f'{log_date} Updated News for : {stock["Symbol"]}')

            stock['is_visible'] = is_visible
            cur.execute(insert_query, stock)
            if cur.rowcount:
                print(f'{log_date} Updated stock for : {stock["Symbol"]}')
        else:
            stock['is_visible'] = True
            cur.execute(insert_query, stock)
            if cur.rowcount:
                inserted_records_count += 1
                print(f'{log_date} Inserted stock for : {stock["Symbol"]}')

    conn.commit()
    cur.close()
    conn.close()

    send_email()
    return inserted_records_count, updated_records_count

def get_all_stocks():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT company_name, symbol, promoters_holdings, fll, dll, government, public, no_of_shares FROM nifty50_stocks WHERE is_visible=true ORDER BY id ASC;")
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

# Ensure the table is created when the module is imported
create_table()
create_news_table()
