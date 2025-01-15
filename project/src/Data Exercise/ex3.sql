-- SQL Script to Calculate Daily Sector Position in USD

-- Step 1: Calculate Daily Position in USD
-- This assumes you have already calculated the daily position in USD
-- as described in the previous exercises.

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

-- Step 2: Join with Company Table
-- We will join the daily position data with the company table to get sector information.

sector_position AS (
    SELECT 
        dp.DATE,
        COALESCE(c.SECTOR_NAME, 'UNKNOWN') AS SECTOR_NAME,
        dp.DAILY_POSITION_USD
    FROM 
        daily_position dp
    LEFT JOIN 
        source.company c
    ON 
        dp.COMPANY_ID = c.ID  -- Assuming ID is the company identifier in the company table
)

-- Step 3: Group by Sector and Date
-- We will group the data by both date and sector to calculate total positions.

SELECT 
    DATE,
    SECTOR_NAME,
    SUM(DAILY_POSITION_USD) AS TOTAL_SECTOR_POSITION_USD,  -- Calculate total position in USD for each sector
        -- Control columns
    CURRENT_TIMESTAMP()                     AS CTRL_INSERT_DATE,   -- Timestamp when query runs
    'TASK_001'                              AS CTRL_TASK_ID,        -- Example task or batch identifier
    'EXTERNAL_SYSTEM'                       AS CTRL_SOURCE_SYSTEM,  -- Example source system
    CURRENT_DATE()                          AS CTRL_PROCESS_DATE,   -- Logical date of processing
    
FROM 
    sector_position
GROUP BY 
    DATE, SECTOR_NAME
ORDER BY 
    DATE, SECTOR_NAME;  -- Order the results by date and sector 