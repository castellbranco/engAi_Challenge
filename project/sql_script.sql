-- SQL Script to Calculate Daily Position in USD with Additional Control Columns EX 1

-- Step 1: Create CTEs for position and price data
WITH position_data AS (
    SELECT 
        p.COMPANY_ID,
        p.DATE,
        p.SHARES
    FROM source.position p
),

price_data AS (
    SELECT 
        pr.COMPANY_ID,
        pr.DATE,
        pr.CLOSE_USD
    FROM source.price pr
)

-- Step 2: Perform the join, calculate daily USD, and add control columns
SELECT 
    pos.COMPANY_ID,
    pos.DATE,
    COALESCE(pos.SHARES, 0)                 AS SHARES,
    COALESCE(pr.CLOSE_USD, 0)               AS CLOSE_USD,
    (COALESCE(pos.SHARES, 0) 
     * COALESCE(pr.CLOSE_USD, 0))           AS DAILY_POSITION_USD,
    
    -- Control columns
    CURRENT_TIMESTAMP()                     AS CTRL_INSERT_DATE,   -- Timestamp when query runs
    'TASK_001'                              AS CTRL_TASK_ID,        -- Example task or batch identifier
    'EXTERNAL_SYSTEM'                       AS CTRL_SOURCE_SYSTEM,  -- Example source system
    CURRENT_DATE()                          AS CTRL_PROCESS_DATE,   -- Logical date of processing
    
    
FROM position_data pos
INNER JOIN price_data pr
    ON pos.COMPANY_ID = pr.COMPANY_ID 
    AND pos.DATE = pr.DATE;

-----------------------------------------------------------------------------------------

-- SQL Script to Identify Top 25% of Companies by Average Position (USD) Over the Last Year Ex 2

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

-----------------------------------------------------------------------------------------

-- SQL Script to Calculate Daily Sector Position in USD Ex 3

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

-----------------------------------------------------------------------------------------