import requests
import sqlite3
import datetime
import time
from decouple import config

# Set your API key here
# API_KEY = '' # Add API Key of your choice
API_KEY = config('API_KEY')

# Setting up SQLite database
def setup_database():
    conn = sqlite3.connect('currency_conversions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY,
            amount REAL,
            from_currency TEXT,
            to_currency TEXT,
            converted_amount REAL,
            conversion_date TEXT
        )
    ''')
    conn.commit()
    return conn

# Caching mechanism for exchange rates
class RateCache:
    def __init__(self):
        self.cache = {}
        self.timestamp = {}

    def get_rate(self, from_currency, to_currency):
        key = (from_currency, to_currency)
        if key in self.cache and (time.time() - self.timestamp[key] < 600):  # 10 minutes
            return self.cache[key]
        return None

    def set_rate(self, from_currency, to_currency, rate):
        key = (from_currency, to_currency)
        self.cache[key] = rate
        self.timestamp[key] = time.time()

# Initialize cache
rate_cache = RateCache()

# Function to fetch live exchange rate
def get_live_rate(from_currency, to_currency):
    cached_rate = rate_cache.get_rate(from_currency, to_currency)
    if cached_rate is not None:
        return cached_rate

    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        rate = data['conversion_rates'].get(to_currency)
        if rate is not None:
            rate_cache.set_rate(from_currency, to_currency, rate)
        return rate
    else:
        print(f"Error fetching live rate: {response.status_code} - {response.text}")
        return None

# Function to fetch historical data for the last 5 days
def get_historical_data(from_currency, to_currency):
    historical_rates = []
    today = datetime.date.today()

    for i in range(1, 6):
        date = today - datetime.timedelta(days=i)
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/history/{from_currency}?start_date={date}&end_date={date}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            rate = data['conversion_rates'].get(to_currency)
            historical_rates.append((date, rate))
        else:
            print(f"Error fetching historical data for {date}: {response.status_code} - {response.text}")
            historical_rates.append((date, None))  # Append None if data is not available

    return historical_rates

# Function to store conversion record
def store_conversion(conn, amount, from_currency, to_currency, converted_amount):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversions (amount, from_currency, to_currency, converted_amount, conversion_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (amount, from_currency, to_currency, converted_amount, datetime.date.today()))
    conn.commit()

# Function to display conversion history
def display_history(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM conversions ORDER BY conversion_date DESC')
    records = cursor.fetchall()
    for record in records:
        print(f"ID: {record[0]}, Amount: {record[1]}, From: {record[2]}, To: {record[3]}, "
              f"Converted Amount: {record[4]}, Date: {record[5]}")

# Main function to run the currency converter
def main():
    conn = setup_database()
    
    while True:
        print("\nCurrency Converter")
        amount = float(input("Enter amount: "))
        from_currency = input("From currency (e.g. USD): ").upper()
        to_currency = input("To currency (e.g. EUR): ").upper()

        # Fetch and display live conversion rate
        live_rate = get_live_rate(from_currency, to_currency)
        if live_rate is not None:
            converted_amount = amount * live_rate
            print(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")
            store_conversion(conn, amount, from_currency, to_currency, converted_amount)

            # Fetch historical data
            historical_data = get_historical_data(from_currency, to_currency)
            print("\nLast 5 days historical data:")
            for date, rate in historical_data:
                if rate is not None:
                    print(f"{date}: {rate:.4f}")
                else:
                    print(f"{date}: Data not available")
        else:
            print("Invalid currency code or unable to fetch the rate.")

        # Ask if the user wants to see conversion history
        view_history = input("\nWould you like to see your conversion history? (yes/no): ").strip().lower()
        if view_history == 'yes':
            display_history(conn)

        # Continue or exit
        continue_conversion = input("\nDo you want to convert another currency? (yes/no): ").strip().lower()
        if continue_conversion != 'yes':
            break

    conn.close()

if __name__ == "__main__":
    main()
