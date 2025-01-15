import os
from dotenv import load_dotenv
import snowflake.connector
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv()

def get_snowflake_connection():
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema=os.getenv('SNOWFLAKE_SCHEMA'),
        role=os.getenv('SNOWFLAKE_ROLE')
    )
    return conn

def run_query(query):
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return pd.DataFrame(results, columns=columns)
    finally:
        cursor.close()
        conn.close()

def visualize_data(df):
    # Group by date and sum all positions to get total portfolio value
    daily_total = df.groupby('DATE')['DAILY_POSITION_USD'].sum().reset_index()
    
    plt.figure(figsize=(12, 6))
    plt.plot(daily_total['DATE'], daily_total['DAILY_POSITION_USD'], 
             marker=None, linestyle='-', color='blue', linewidth=2)
    
    plt.title('Total Portfolio Value Over Time')
    plt.xlabel('Date')
    plt.ylabel('Total Position (USD)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Format y-axis to show billions
    plt.gca().yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f'${x/1e9:.1f}B'))
    
    plt.show()

if __name__ == "__main__":
    sql_query = """
    WITH position_data AS (
        SELECT 
            p.COMPANY_ID,
            p.DATE,
            p.SHARES
        FROM 
            source.position p
    ),
    price_data AS (
        SELECT 
            pr.COMPANY_ID,
            pr.DATE,
            pr.CLOSE_USD
        FROM 
            source.price pr
    )
    SELECT 
        pos.COMPANY_ID,
        pos.DATE,
        COALESCE(pos.SHARES, 0) AS SHARES,
        COALESCE(pr.CLOSE_USD, 0) AS CLOSE_USD,
        (COALESCE(pos.SHARES, 0) * COALESCE(pr.CLOSE_USD, 0)) AS DAILY_POSITION_USD
    FROM 
        position_data pos
    INNER JOIN 
        price_data pr
    ON 
        pos.COMPANY_ID = pr.COMPANY_ID AND pos.DATE = pr.DATE;
    """
    data_frame = run_query(sql_query)
    visualize_data(data_frame)