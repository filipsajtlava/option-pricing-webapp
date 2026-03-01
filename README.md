# Option Pricing WebApp

A web application for pricing financial options and visualizing option data, built with Python and Streamlit. The app provides both Black-Scholes and Monte Carlo simulation pricing models and integrates with Supabase for data storage and updates. Option data is fetched using yfinance and processed for analysis, visualization, and educational purposes.

![Real options pricing interface](images/pricing.png)

## Link

The project is easily accessible through the official streamlit deployment:
- [Option Pricing WebApp](https://option-pricing-webapp-c8y6rhi4qgmxgkvannfxar.streamlit.app/)

## Features

- **Option Pricing Models:**  
  - Black-Scholes formula,
  - Monte Carlo simulation (with confidence intervals and path plotting).

- **Data Integration:**  
  - Fetches live option chain data for S&P 500 tickers via yfinance,
  - Stores and updates option snapshots in Supabase.

- **Visualizations:**  
  - Plots for modelled price, confidence intervals, and historical asset prices (candlestick plots),
  - Display of option Greeks and sensitivity analysis.

- **User Interface:**  
  - Interactive controls for all model parameters via Streamlit sliders and inputs,
  - Tabs for different pricing approaches and practical option pricing.

![Part of Monte Carlo simulation](images/mc.gif)

## Technologies used

- **Python**
- **Streamlit** for the web interface
- financial data fetching from **yfinance**
- **pandas, numpy**
- graphics made using **plotly**
- **Supabase** as a backend database (saving actual market prices)

## Getting Started

In case you want to download the application, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/filipsajtlava/option-pricing-webapp.git
   cd option-pricing-webapp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

## Project Structure

- `app.py` — main streamlit application,
- `config.py` — configuration file,
- `supabase_updater/` — scripts for fetching and updating option data,
- `pricing/` — option models and financial calculations,
- `plotting/` — plotting utilities for visualizations,
- `src/` — UI components and utility functions.

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [yfinance](https://github.com/ranaroussi/yfinance)
- [Supabase](https://supabase.com/)
