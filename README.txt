# Project Structure
engAi_Challenge/
│
├── project/
│   ├── app.py                             # Main Streamlit application file
│   ├── sql_script.sql                     # SQL script with data queries
│   │
│   ├── src/
│   │   ├── Backend/
│   │   │   ├── snowflake_connection.py    # Contains functions to connect to Snowflake
│   │   │   └── data_queries.py            # Contains functions for querying data from Snowflake
│   │   │
│   │   ├── Data Exercise/
│   │   │   ├── ex1.sql                    # SQL script for Exercise 1
│   │   │   ├── ex2.sql                    # SQL script for Exercise 2
│   │   │   └── ex3.sql                    # SQL script for Exercise 3
│   │   │
│   │   └── Query Visualization/
│   │       ├── run_query_ex1.py           # Script to visualize total portfolio value over time
│   │       ├── run_query_ex2.py           # Script to visualize top companies by average position
│   │       └── run_query_ex3.py           # Script to visualize sector positions over time
│   │
│   └── .env                               # Environment variables for Snowflake connection
│
├── .gitignore                             # Specifies files and directories to ignore in Git
├── requirements.txt                       # List of Python package dependencies
└── README.md                              # Documentation for the project



# BI Dashboard

This project is a Business Intelligence (BI) Dashboard that connects to a Snowflake database to visualize company and sector data. It uses Streamlit for the web interface and Plotly for interactive visualizations.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- Snowflake account and credentials
- Basic knowledge of Python and SQL

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/castellbranco/engAi_Challenge.git
   cd engAi_Challenge
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv engAI
   ```

3. **Activate the virtual environment:**

   - On Windows:
     ```bash
     .\engAI\Scripts\activate
     ```

   - On macOS/Linux:
     ```bash
     source engAI/bin/activate
     ```

4. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**

   Create a `.env` file in the root directory of the project and add your Snowflake credentials:

   ```plaintext
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=your_schema
   SNOWFLAKE_ROLE=your_role
   ```

## Usage

1. **Run the Streamlit app:**

   ```bash
   streamlit run app.py
   ```

2. **Open your web browser and go to:**

   ```
   http://localhost:8501
   ```

3. **Interact with the dashboard:**
   - Select sectors and companies to visualize data.
   - Use the date inputs to filter the data.
   - Export data as CSV files.

## Exporting Data

You can export the following data from the dashboard:

- Top 25% Companies
- Company Timeseries
- Top 10 Sectors

Simply select the desired data from the dropdown menu and click the export button.


1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.
