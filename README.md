# Currency Converter

A simple terminal-based currency converter that allows users to perform live currency conversions and fetch historical data for the last 5 days of the conversion.

## Features

- Live currency conversion based on user input
- Historical data for the last 5 days
- SQLite database for storing conversion history

## Requirements

- Python 3.x
- `requests` library

## Setup

1. Clone this repository or download the files.
2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv

**NOTE**: Delete the .venv directory and run the file currency_converter.py by creating a new venv or after removing .venv install the dependencies globally. Since app.exchangerate-api.com doesn't provide past 5 days historical data for the same conversion its will show data not found in the result. But it will work properly for other websites which provides the past value data.
   