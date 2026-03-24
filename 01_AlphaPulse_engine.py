import yfinance as yf
import pandas as pd
import numpy as np

# --- STEP 1: THE DATA SCRAPER ---
print("🚀 Phase 1: Gathering Market Data...")
tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'JPM', 'V', 'PG', 'JNJ', 'XOM', '^GSPC']
raw_data = yf.download(tickers, start="2024-01-01", end="2026-03-24")['Close']
data = raw_data.ffill() 
data.to_csv('portfolio_prices.csv')
print("✅ Saved: portfolio_prices.csv")

# --- STEP 2: QUANTITATIVE ANALYSIS ---
print("📊 Phase 2: Running Financial Math...")
returns = np.log(data / data.shift(1)).dropna()

# Correlation Matrix
corr_matrix = returns.corr()
corr_matrix.to_csv('correlation_matrix.csv')

# Rolling Volatility (30-day window)
volatility = returns.rolling(window=30).std() * np.sqrt(252)
volatility.to_csv('rolling_volatility.csv')
print("✅ Saved: Math Files")

# --- STEP 3: MONTE CARLO SIMULATION ---
print("🎲 Phase 3: Predicting the Future (Monte Carlo)...")
simulations = 10000
days = 252 
weights = np.array([0.1] * 10) 
portfolio_returns = returns.drop(columns=['^GSPC'])

mean_returns = portfolio_returns.mean()
cov_matrix = portfolio_returns.cov()
chol_decomp = np.linalg.cholesky(cov_matrix)

simulation_results = np.zeros((days, simulations))

for i in range(simulations):
    z = np.random.normal(size=(days, 10))
    daily_stock_returns = np.dot(z, chol_decomp.T) + mean_returns.values
    
    # THE FIX: This combines 10 stocks into 1 portfolio number
    portfolio_daily_returns = np.dot(daily_stock_returns, weights)
    
    # Starting at $1 and growing
    simulation_results[:, i] = np.cumprod(1 + portfolio_daily_returns)

# Save for Tableau
pd.DataFrame(simulation_results).to_csv('monte_carlo_results.csv')

# Success Message
final_values = simulation_results[-1, :]
var_95_level = np.percentile(final_values, 5)
print(f"✅ ALL DONE! 5% VaR is: {round((1 - var_95_level)*100, 2)}%")