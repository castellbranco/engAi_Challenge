-- SQL Script to Calculate Daily Position in USD with Additional Control Columns

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
