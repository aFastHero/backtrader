# Import package
import yfinance as yf

# Get the data
data = yf.download(tickers="TSLA", period="1d", interval="1h", prepost=True)

# Print the data
print(data)