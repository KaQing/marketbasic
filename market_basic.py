# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 18:22:42 2024

@author: fisch
"""
import yfinance as yf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.support.ui import Select
import pandas as pd
import string
from selenium.webdriver.common.action_chains import ActionChains
import matplotlib.pyplot as plt

# Get the current price of the Futures
def get_ticker_price(ticker):
    # Create a ticker object
    ticker_obj = yf.Ticker(ticker)
    
    # Fetch the current price
    data = ticker_obj.info  # Fetches the latest trading day data
    current_price = data['bid']  # Get the last close price

    return current_price

# Define function to delete empty spaces and replace commas with point decimals
def clean_price(price):
    if pd.isna(price):
        return None
    # Remove any non-numeric characters except for decimal point
    return str(price).replace(' ', '').replace(',', '.')

# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-default-apps")
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-search-engine-choice-screen")


# Initialize WebDriver with options
driver = webdriver.Chrome(options=options)


# Open DXS frontpage
driver.get("https://dxs.app/market/")

# Maximize the window (optional, but might help with clicking)
driver.maximize_window()

# Wait for the page to load properly
time.sleep(1)  # Adjust sleep time based on your needs

# Remove the preview screen by clicking outside
# Assuming we click somewhere on the side of the screen to close the preview
actions = ActionChains(driver)

# Move to the top-left corner of the page and click
actions.move_by_offset(0, 0).click().perform() 
time.sleep(1)  # Pause to ensure the screen is removed

# Locate the COMMODITIES button by its class name and click
commodities_button = driver.find_element(By.XPATH, "//div[contains(@class, 'max') and contains(@class, 'tab-button') and text()='COMMODITIES']")
commodities_button.click()

# Wait to observe the result (optional)
time.sleep(1)

# Find all pairs by the class 'markets-table__field-name-ticker'
pairs = driver.find_elements(By.CLASS_NAME, 'markets-table__field-name-ticker')

# Find all prices by the class 'markets-table__field-price'
prices = driver.find_elements(By.CLASS_NAME, 'markets-table__field-price')

# Extract the text for pairs and prices
pair_list = [pair.text for pair in pairs]
price_list = [price.text for price in prices]

# Close the browser
driver.quit()

# Create a Pandas DataFrame
df = pd.DataFrame({
    'DXS_ticker': pair_list,
    'DXS_price': price_list,
})

# Drop rows where 'DXS_ticker' or 'YF_ticker' equals 'XAU/XAG'
df = df[df['DXS_ticker'] != 'XAU/XAG']

# Ticker dictionary
ticker_dict = {
    "HG": "HG=F",
    "WTICO": "CL=F",
    "XAU": "GC=F",
    "NATGAS": "NG=F",
    "XPD": "PA=F",
    "XPT": "PL=F",
    "XAG": "SI=F",
    "ZC": "ZC=F",
    "ZW": "ZW=F"
}

# Map the 'DXS_ticker' column to the 'ticker_dict' to update 'YF_ticker'
df['YF_ticker'] = df['DXS_ticker'].map(ticker_dict)

# Iterate through each row of the dataframe and get the ticker price of the futures
for index, row in df.iterrows():
    yf_ticker = row["YF_ticker"]
    yf_price = get_ticker_price(yf_ticker)
    df.at[index, "YF_price"] = yf_price

# Clean the price data
df['DXS_price'] = df['DXS_price'].apply(clean_price)
df['YF_price'] = df['YF_price'].apply(clean_price)

# Convert columns to numeric
df['DXS_price'] = pd.to_numeric(df['DXS_price'], errors='coerce')
df['YF_price'] = pd.to_numeric(df['YF_price'], errors='coerce')

# Specify the indices of rows which need to be multiplied
indices_to_update = [8, 9]  # Example indices

# Multiply the specified values in 'YF_price' by 100
df.loc[indices_to_update, 'DXS_price'] *= 100

df["market_basic [%]"] = (1 - (df["DXS_price"] / df["YF_price"])) * 100

# Show the DataFrame
print(df)

plt.bar(df["YF_ticker"], df["market_basic [%]"])
plt.show()
