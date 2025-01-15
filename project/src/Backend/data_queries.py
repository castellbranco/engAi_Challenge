import pandas as pd
from snowflake.connector.cursor import SnowflakeCursor
from typing import List
import streamlit as st
#Calculate Daily Position in USD
def calculate_daily_position(cursor: SnowflakeCursor) -> pd.DataFrame:
    query = """
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
        pos.COMPANY_ID = pr.COMPANY_ID AND pos.DATE = pr.DATE
    """
    cursor.execute(query)
    # Convert results to pandas DataFrame
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(results, columns=columns)

@st.cache_data
def calculate_top_sectors(_cursor: SnowflakeCursor, start_date: str, end_date: str, selected_sectors: List[str]) -> pd.DataFrame:
    if not selected_sectors:
        return pd.DataFrame(columns=['SECTOR_NAME', 'TOTAL_POSITION_USD'])

    query = f"""
    WITH daily_position AS (
        SELECT 
            p.DATE,
            c.SECTOR_NAME,
            COALESCE(p.SHARES, 0) * COALESCE(pr.CLOSE_USD, 0) AS DAILY_POSITION_USD
        FROM 
            source.position p
        INNER JOIN 
            source.price pr ON p.COMPANY_ID = pr.COMPANY_ID AND p.DATE = pr.DATE
        INNER JOIN
            source.company c ON p.COMPANY_ID = c.ID
        WHERE 
            p.DATE BETWEEN '{start_date}' AND '{end_date}'
            AND c.SECTOR_NAME IN ({','.join([f"'{sector}'" for sector in selected_sectors])})
    ),
    top_sectors AS (
        SELECT 
            DATE,
            SECTOR_NAME,
            SUM(DAILY_POSITION_USD) AS TOTAL_POSITION_USD
        FROM 
            daily_position
        GROUP BY
            DATE, SECTOR_NAME
    )
    SELECT 
        SECTOR_NAME,
        SUM(TOTAL_POSITION_USD) AS TOTAL_POSITION_USD
    FROM
        top_sectors
    GROUP BY
        SECTOR_NAME
    ORDER BY
        TOTAL_POSITION_USD DESC
    LIMIT 10
    """
    _cursor.execute(query)
    results = _cursor.fetchall()
    columns = [desc[0] for desc in _cursor.description]
    return pd.DataFrame(results, columns=columns)

def fetch_top_companies(cursor: SnowflakeCursor) -> pd.DataFrame:
    query = """
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
    ),
    top_25_percent AS (
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
    )
    SELECT 
        c.TICKER,
        c.SECTOR_NAME,
        p.SHARES,
        pr.CLOSE_USD AS LAST_CLOSE_PRICE_USD,
        t.AVERAGE_POSITION_USD
    FROM 
        top_25_percent t
    INNER JOIN 
        source.company c ON t.COMPANY_ID = c.ID
    INNER JOIN 
        source.position p ON t.COMPANY_ID = p.COMPANY_ID
    INNER JOIN 
        source.price pr ON t.COMPANY_ID = pr.COMPANY_ID
    WHERE 
        p.DATE = (SELECT MAX(DATE) FROM source.position)
        AND pr.DATE = (SELECT MAX(DATE) FROM source.price)
    ORDER BY 
        t.AVERAGE_POSITION_USD DESC;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(results, columns=columns)

def fetch_company_list(cursor: SnowflakeCursor) -> pd.DataFrame:
    query = """
    SELECT DISTINCT TICKER
    FROM source.company
    """
    cursor.execute(query)
    results = cursor.fetchall()
    return [row[0] for row in results]

def fetch_timeseries_data(cursor: SnowflakeCursor, company_ticker: str) -> pd.DataFrame:
    query = f"""
    SELECT 
        p.DATE,
        p.CLOSE_USD
    FROM 
        source.price p
    INNER JOIN 
        source.company c ON p.COMPANY_ID = c.ID
    WHERE 
        c.TICKER = '{company_ticker}'
    ORDER BY 
        p.DATE
    """
    cursor.execute(query)
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(results, columns=columns)

@st.cache_data
def fetch_sector_list(_cursor: SnowflakeCursor) -> List[str]:
    query = """
    SELECT DISTINCT SECTOR_NAME
    FROM source.company
    """
    _cursor.execute(query)
    results = _cursor.fetchall()
    return [row[0] for row in results]

def fetch_latest_date(cursor: SnowflakeCursor) -> str:
    query = """
    SELECT MAX(DATE) AS LATEST_DATE
    FROM source.position
    """
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0].strftime('%Y-%m-%d') 