USE retail_supply_chain;

SELECT
    COUNT(DISTINCT StockCode) AS distinct_products
FROM stg_eligible_sales;

SELECT
    StockCode,
    COUNT(DISTINCT TRIM(Description)) AS description_variants
FROM stg_eligible_sales
GROUP BY StockCode
HAVING COUNT(DISTINCT TRIM(Description)) > 1
ORDER BY description_variants DESC, StockCode
LIMIT 10;