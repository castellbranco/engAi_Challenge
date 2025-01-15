-- SQL Script to Identify Top 25% of Companies by Average Position (USD) Over the Last Year

-- Step 1: Calculate Daily Position in USD
-- This assumes you have already calculated the daily position in USD
-- as described in the previous exercise.

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

-- Step 2: Filter Data for the Last Year
-- We will filter the daily position data to include only records
-- from the last year based on the most recent date available.

last_year_data AS (
    SELECT 
        COMPANY_ID,
        DAILY_POSITION_USD
    FROM 
        daily_position
    WHERE 
        DATE >= DATEADD(YEAR, -1, (SELECT MAX(DATE) FROM source.position))
-- Adjusting for the last year
)

-- Step 3: Calculate Average Position in USD for Each Company
-- Grouping by COMPANY_ID to calculate the average daily position.

, average_position AS (
    SELECT 
        COMPANY_ID,
        AVG(DAILY_POSITION_USD) AS AVERAGE_POSITION_USD
    FROM 
        last_year_data
    GROUP BY 
        COMPANY_ID
)

-- Step 4: Determine the 25% Cutoff
-- Using NTILE to rank companies based on their average position.

SELECT 
    COMPANY_ID,
    AVERAGE_POSITION_USD,
            -- Control columns
    CURRENT_TIMESTAMP()                     AS CTRL_INSERT_DATE,   -- Timestamp when query runs
    'TASK_001'                              AS CTRL_TASK_ID,        -- Example task or batch identifier
    'EXTERNAL_SYSTEM'                       AS CTRL_SOURCE_SYSTEM,  -- Example source system
    CURRENT_DATE()                          AS CTRL_PROCESS_DATE,   -- Logical date of processing
FROM 
    (
        SELECT 
            COMPANY_ID,
            AVERAGE_POSITION_USD,
            NTILE(4) OVER (ORDER BY AVERAGE_POSITION_USD DESC) AS POSITION_RANK
        FROM 
            average_position
    ) ranked_companies

WHERE 
    POSITION_RANK = 1  -- Selecting the top 25%
ORDER BY 
    AVERAGE_POSITION_USD DESC;  -- Order by average position in USD 