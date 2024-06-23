import psycopg2
from psycopg2 import sql
from datetime import datetime
from decimal import Decimal


# Database connection setup
def connect_db():
    return psycopg2.connect(
        dbname='stocks',
        user='postgres',
        password='password',
        host='0.0.0.0'
    )

def create_table():
    conn = connect_db()
    cur = conn.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS nifty50_stocks (
        id SERIAL PRIMARY KEY,
        company_name TEXT,
        industry TEXT,
        symbol TEXT UNIQUE,
        price DECIMAL(20,2),
        market_cap DECIMAL(20,2),
        promoters_holdings DECIMAL(20,2),
        dll DECIMAL(20,2),
        fll DECIMAL(20,2),
        government DECIMAL(20,2),
        public DECIMAL(20,2),
        no_of_shares DECIMAL(20,2),
        is_visible BOOLEAN DEFAULT FALSE,
        created_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        id SERIAL PRIMARY KEY,
        stock_id INTEGER REFERENCES nifty50_stocks(id),
        heading TEXT NOT NULL,
        description TEXT NOT NULL,
        created_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        %(Company Name)s, %(Industry)s, %(Symbol)s, %(Price)s, %(Market Cap)s,
        %(Promoters Holdings)s, %(DLL)s, %(FLL)s, %(Government)s, %(Public)s, %(No of Shares)s, %(Date)s, %(Last Updated)s, %(is_visible)s
    )
    ON CONFLICT (symbol) DO UPDATE SET
        price = EXCLUDED.price,
        market_cap = EXCLUDED.market_cap,
        promoters_holdings = EXCLUDED.promoters_holdings,
        dll = EXCLUDED.dll,
        fll = EXCLUDED.fll,
        government = EXCLUDED.government,
        public = EXCLUDED.public,
        no_of_shares = EXCLUDED.no_of_shares,
        last_updated = EXCLUDED.last_updated,
        is_visible = EXCLUDED.is_visible
    RETURNING id, symbol;
    '''

    news_insert_query = '''
    INSERT INTO news (stock_id, heading, description, created_dt)
    VALUES (%s, %s, %s, %s);
    '''

    inserted_records_count = 0
    updated_records_count  = 0

    for stock in stock_data:
        stock['Date'] = datetime.now()
        stock['Last Updated'] = datetime.now()

        cur.execute(fetch_query, (stock['Symbol'],))
        existing_data = cur.fetchone()

        if existing_data:
            stock_id, existing_market_cap, existing_promoters_holdings, existing_dll, existing_fll, existing_government, existing_public, existing_no_of_shares = existing_data
            existing_market_cap = Decimal(existing_market_cap) if existing_market_cap is not None else None
            existing_promoters_holdings = Decimal(existing_promoters_holdings) if existing_promoters_holdings is not None else None
            existing_dll = Decimal(existing_dll) if existing_dll is not None else None
            existing_fll = Decimal(existing_fll) if existing_fll is not None else None
            existing_government = Decimal(existing_government) if existing_government is not None else None
            existing_public = Decimal(existing_public) if existing_public is not None else None
            existing_no_of_shares = Decimal(existing_no_of_shares) if existing_no_of_shares is not None else None

            message_parts = []
            is_visible = False

            if stock['Market Cap'] is not None and existing_market_cap is not None:
                if stock['Market Cap'] != existing_market_cap:
                    if stock['Market Cap'] < existing_market_cap:
                        message_parts.append(f"Market Cap value decreased, Prev: {existing_market_cap:.0f} Last: {stock['Market Cap']:.0f}")
                    else:
                        message_parts.append(f"Market Cap value increased, Prev: {existing_market_cap:.0f} Last: {stock['Market Cap']:.0f}")
                        is_visible = True

            if stock['Promoters Holdings'] is not None and existing_promoters_holdings is not None:
                if stock['Promoters Holdings'] != existing_promoters_holdings:
                    if stock['Promoters Holdings'] < existing_promoters_holdings:
                        message_parts.append("Promoters holdings decreased, Prev: " + str(existing_promoters_holdings) + " Last: " + str(stock['Promoters Holdings']) )
                    else:
                        message_parts.append("Promoters holdings increased, Prev: " + str(existing_promoters_holdings) + " Last: " + str(stock['Promoters Holdings']) )
                        is_visible = True

            if stock['DLL'] is not None and existing_dll is not None:
                if stock['DLL'] != existing_dll:
                    if stock['DLL'] < existing_dll:
                        message_parts.append("DLL holding decreased, Prev: " + str(existing_dll) + " Last: " + str(stock['DLL']) )
                    else:
                        message_parts.append("DLL holding increased, Prev: " + str(existing_dll) + " Last: " + str(stock['DLL']) )
                        is_visible = True

            if stock['FLL'] is not None and existing_fll is not None:
                if stock['FLL'] != existing_fll:
                    if stock['FLL'] < existing_fll:
                        message_parts.append("FLL holding decreased, Prev: " + str(existing_fll) + " Last: " + str(stock['FLL']) )
                    else:
                        message_parts.append("FLL holding increased, Prev: " + str(existing_fll) + " Last: " + str(stock['FLL']) )
                        is_visible = True

            if stock['Government'] is not None and existing_government is not None:
                if stock['Government'] != existing_government:
                    if stock['Government'] < existing_government:
                        message_parts.append("Government holding decreased, Prev: " + str(existing_government) + " Last: " + str(stock['Government']) )
                    else:
                        message_parts.append("Government holding increased, Prev: " + str(existing_government) + " Last: " + str(stock['Government']) )
                        is_visible = True

            if stock['Public'] is not None and existing_public is not None:
                if stock['Public'] != existing_public:
                    if stock['Public'] < existing_public:
                        message_parts.append("Public holding decreased, Prev: " + str(existing_public) + " Last: " + str(stock['Public']) )
                    else:
                        message_parts.append("Public holding increased, Prev: " + str(existing_public) + " Last: " + str(stock['Public']) )
                        is_visible = True

            if stock['No of Shares'] is not None and existing_no_of_shares is not None:
                if stock['No of Shares'] != existing_no_of_shares:
                    if stock['No of Shares'] < existing_no_of_shares:
                        message_parts.append("No of Shareholders decreased, Prev: " + str(existing_no_of_shares) + " Last: " + str(stock['No of Shares']) )
                    else:
                        message_parts.append("No of Shareholders increased, Prev: " + str(existing_no_of_shares) + " Last: " + str(stock['No of Shares']) )
                        is_visible = True

            if message_parts:
                updated_records_count += 1
                heading = f"Alert for {stock['Symbol']}"
                description = "\n ".join(message_parts)
                created_dt = datetime.now()
                cur.execute(news_insert_query, (stock_id, heading, description, created_dt))
                print(f'Updated News for : {stock["Symbol"]}')

            stock['is_visible'] = is_visible
            cur.execute(insert_query, stock)
            result = cur.fetchone()
            if result:
                print(f'Updated stock for : {stock["Symbol"]}')
        else:
            stock['is_visible'] = True
            cur.execute(insert_query, stock)
            result = cur.fetchone()
            if result:
                inserted_records_count += 1
                print(f'Inserted stock for : {stock["Symbol"]}')

    conn.commit()
    cur.close()
    conn.close()

    return inserted_records_count, updated_records_count

def get_all_stocks():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT company_name,symbol, promoters_holdings, fll, dll, government, public, no_of_shares FROM nifty50_stocks WHERE is_visible=true order by id asc;")
    stocks = cur.fetchall()
    cur.close()
    conn.close()
    return stocks

def get_all_news():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM news order by id desc;")
    news = cur.fetchall()
    cur.close()
    conn.close()
    return news

# Ensure the table is created when the module is imported
create_table()
create_news_table()
