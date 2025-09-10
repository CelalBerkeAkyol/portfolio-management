# Advanced Portfolio Analysis Toolkit

An integrated suite of Python scripts and a modern web dashboard for comprehensive investment portfolio tracking, analysis, and strategic planning.

![Screenshot of the Main Dashboard](./images/Screenshot%202025-09-07%20at%2019.59.20.png)
![Screenshot of the Main Dashboard](./images/Screenshot%202025-09-07%20at%2019.36.49.png)

## Introduction

Effective investment management goes beyond simply acquiring assets; it requires consistent tracking, risk assessment, and strategic alignment with financial goals. This toolkit provides a powerful solution to manage and analyze investment portfolios by bridging the gap between raw data and actionable insights.

It uses a set of Python scripts for robust data management and a dynamic, browser-based dashboard for intuitive visualization. Users can track their current holdings, compare them against target and base allocations, perform scenario analysis, and assess their risk profile, all within a unified ecosystem.

## Features

- **Detailed Portfolio Tracking:** Log current asset values and see their real-time percentage distribution.
- **Goal-Oriented Comparison:** Compare your **Current Portfolio** against a pre-defined **Target Portfolio** to identify rebalancing opportunities.
- **Core-Satellite Strategy:** Define a **Base Portfolio** representing your core, long-term, fixed holdings.
- **Multi-Scenario Analysis:** Project your portfolio's potential performance and final value under **Bad, Base, and Good** market scenarios.
- **Risk Assessment:** Calculate a weighted average risk score for your portfolio and assess your personal risk tolerance with an interactive questionnaire.
- **Interactive Web Dashboard:** A modern frontend that visualizes your portfolio with side-by-side pie charts, a clear "Buy/Sell" actions table, and comparative analytics.

## Project Components

The project is organized into three main directories: `data` for storing information, `python` for backend logic, and `web` for the user-facing applications.

### 1. Data Files (`/data/`)

These JSON files serve as the central database for the entire toolkit.

- **`asset_info.json`**: This is the core "assumptions engine." It stores the intrinsic financial characteristics for every asset class, including its `risk_score` and expected returns for different market scenarios (`bad_scenario_return`, `expected_percentage_return`, `good_scenario_return`).

- **`people.json`**: This file acts as the user database. Each person is an object containing a detailed snapshot of their financial profile. The main keys are:
  - **`name`**: The full name of the portfolio owner.
  - **`risk_score`**: The calculated risk tolerance score, typically generated from the risk questionnaire.
  - **`principal`**: The total current market value of the portfolio in TL.
  - **`target_portfolio`**: A user-defined dictionary of assets and their ideal percentages. This is used as the benchmark for rebalancing.
  - **`current_values` / `current_values`**: The current market value (in TL) of each asset held. This data is primarily updated by the `current_portfolio.py` script.
  - **`current_portfolio` / `current_portfolio`**: The calculated percentage distribution of the current holdings, derived from `current_values`.

### 2. Python Scripts (`/python/`)

These scripts handle data manipulation, updates, and console-based reporting.

- **`current_portfolio.py`**: The primary script for **updating current holdings**. It runs a command-line interface (CLI) that prompts the user to enter the latest TL value for each asset. It then recalculates all distributions and saves the updated data back to `people.json`.

- **`comparison_report.py`**: A powerful CLI tool that generates a detailed text-based report comparing the **Current, Base, and Target** portfolios. It calculates and displays buy/sell actions and runs a comparative scenario analysis.

- **`target_portfolio.py`**: A simpler script that reads the `target_portfolio` for a selected user and generates a report on its structure, risk, and expected return.

- **`/risk_calculation/`**: This sub-directory contains tools for assessing risk.
  - **`risk_survey.json`**: Stores the questions and scoring for the risk profile questionnaire.
  - **`personal_risk.py`**: A CLI script that runs the risk survey and calculates a final risk score for the user.

### 3. Web Applications (`/web/`)

These self-contained HTML files provide the modern, visual interface for the toolkit.

- **`risk-testi.html`**: An interactive, web-based version of the risk questionnaire. It presents the survey from `risk_survey.json` in a user-friendly format, calculates the score, and displays the corresponding risk profile (e.g., Conservative, Moderate, Aggressive).

- **`portfolio_displayer.html`**: The main dashboard. This application reads the data from the JSON files and provides a complete visual analysis, including:
  - A dropdown menu to select a person from `people.json`.
  - Side-by-side pie charts for **Current vs. Target** distributions.
  - A "Rebalancing Actions" table detailing the exact buy/sell amounts required to reach the target.
  - A comparative scenario analysis for both portfolios.

## How to Use

### 1. Project Setup

Ensure your project has the following file structure:

```
/portföy/
├── 📂 data/
│   ├── asset_info.json
│   └── people.json
├── 📂 python/
│   ├── 📂 risk_calculation/
│   │   ├── personal_risk.py
│   │   └── risk_survey.json
│   ├── comparison_report.py
│   ├── current_portfolio.py
│   └── target_portfolio.py
├── 📂 web/
│   ├── portfolio_displayer.html
│   └── risk-testi.html
└── 📜 README.md
```

### 2. Running the Python Scripts

Navigate to the `python` directory in your terminal to run the scripts.

```bash
# Go into the python directory
cd python

# Run a script, for example:
python current_portfolio.py
```

### 3. Running the Web Application

The web applications must be run via a **local server**.

1.  Open your terminal in the **root directory** of the project (the `portföy` folder).
2.  Run the built-in Python web server with this command:
    ```bash
    # For Python 3
    python -m http.server
    ```
3.  Open your web browser and navigate to one of the following URLs:
    - For the main dashboard: **`http://localhost:8000/web/portfolio_displayer.html`**
    - For the risk test: **`http://localhost:8000/web/risk-testi.html`**

Now, whenever you update your `people.json` or `asset_info.json` files, you only need to **refresh the web page** to see the changes instantly.
