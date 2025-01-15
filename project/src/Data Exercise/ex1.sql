-- SQL Script to Calculate Daily Position in USD

-- Step 1: Select relevant columns from both tables
-- We will join the source.position and source.price tables
-- based on the COMPANY_ID and DATE columns.

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

-- Step 2: Join the position and price data
-- We will use an INNER JOIN to ensure we only get records
-- where both position and price data are available.

SELECT 
    pos.COMPANY_ID,
    pos.DATE,
    COALESCE(pos.SHARES, 0) AS SHARES,  -- Handle missing shares by replacing NULL with 0
    COALESCE(pr.CLOSE_USD, 0) AS CLOSE_USD,  -- Handle missing USD price by replacing NULL with 0
    (COALESCE(pos.SHARES, 0) * COALESCE(pr.CLOSE_USD, 0)) AS DAILY_POSITION_USD  -- Calculate daily position in USD
FROM 
    position_data pos
INNER JOIN 
    price_data pr
ON 
    pos.COMPANY_ID = pr.COMPANY_ID AND pos.DATE = pr.DATE

-- Step 3: Handle missing data
-- In this query, we are using COALESCE to replace NULL values with 0 for both shares and USD price.
-- This ensures that we can still calculate a daily position even if one of the values is missing.

-- Step 4: Final output
-- The result will include COMPANY_ID, DATE, SHARES, CLOSE_USD, and DAILY_POSITION_USD.
