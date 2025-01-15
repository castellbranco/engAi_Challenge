import os
from dotenv import load_dotenv
import snowflake.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

def visualize_sector_positions(df):
    plt.figure(figsize=(12, 6))
    
    # Create horizontal bar chart
    bars = plt.barh(df['SECTOR_NAME'], df['TOTAL_SECTOR_POSITION_USD'] / 1e9, color='skyblue')
    
    # Customize the plot
    plt.title('Total Sector Position in USD', fontsize=16, pad=20)
    plt.xlabel('Total Position (Billion USD)', fontsize=12)
    
    # Add value labels on the bars
    for bar in bars:
        width = bar.get_width()
        plt.text(width + (width * 0.01), bar.get_y() + bar.get_height()/2,
                 f'${width:.2f}B', ha='left', va='center', fontweight='bold')
    
    plt.grid(True, axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    sql_query = """
    WITH daily_position AS (
        SELECT 
            pos.COMPANY_ID,
            pos.DATE,
            COALESCE(pos.SHARES, 0) * COALESCE(pr.CLOSE_USD, 0) AS DAILY_POSITION_USD
        FROM 
            source.position pos
        INNER JOIN 
            source.price pr
        ON 
            pos.COMPANY_ID = pr.COMPANY_ID AND pos.DATE = pr.DATE
    ),
    sector_position AS (
        SELECT 
            dp.DATE,
            c.SECTOR_NAME,
            dp.DAILY_POSITION_USD
        FROM 
            daily_position dp
        INNER JOIN 
            source.company c
        ON 
            dp.COMPANY_ID = c.ID
    )
    SELECT 
        DATE,
        SECTOR_NAME,
        SUM(DAILY_POSITION_USD) AS TOTAL_SECTOR_POSITION_USD
    FROM 
        sector_position
    GROUP BY 
        DATE, SECTOR_NAME
    ORDER BY 
        DATE, SECTOR_NAME;
    """
    
    data_frame = run_query(sql_query)
    visualize_sector_positions(data_frame)