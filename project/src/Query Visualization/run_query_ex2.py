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

def visualize_top_companies(df):
    plt.figure(figsize=(12, 6))
    
    # Create horizontal bar chart
    bars = plt.barh(range(len(df)), 
                   df['AVERAGE_POSITION_USD'] / 1e9,  # Convert to billions
                   color='skyblue')
    
    # Customize the plot
    plt.title('Top 25% Companies by Average Position', pad=20)
    plt.xlabel('Average Position (Billion USD)')
    plt.ylabel('Company ID')
    
    # Add value labels on the bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, 
                bar.get_y() + bar.get_height()/2,
                f'${width:.2f}B',
                ha='left', 
                va='center',
                fontweight='bold')
    
    # Set y-ticks to company IDs
    plt.yticks(range(len(df)), df['COMPANY_ID'])
    
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
    last_year_data AS (
        SELECT 
            COMPANY_ID,
            DAILY_POSITION_USD
        FROM 
            daily_position
        WHERE 
            DATE >= DATEADD(YEAR, -1, CURRENT_DATE())
    ),
    average_position AS (
        SELECT 
            COMPANY_ID,
            AVG(DAILY_POSITION_USD) AS AVERAGE_POSITION_USD
        FROM 
            last_year_data
        GROUP BY 
            COMPANY_ID
    )
    SELECT 
        COMPANY_ID,
        AVERAGE_POSITION_USD
    FROM (
        SELECT 
            COMPANY_ID,
            AVERAGE_POSITION_USD,
            NTILE(4) OVER (ORDER BY AVERAGE_POSITION_USD DESC) AS POSITION_RANK
        FROM 
            average_position
    ) ranked_companies
    WHERE 
        POSITION_RANK = 1
    ORDER BY 
        AVERAGE_POSITION_USD DESC;
    """
    
    data_frame = run_query(sql_query)
    visualize_top_companies(data_frame) 