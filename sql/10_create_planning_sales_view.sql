USE retail_supply_chain;

CREATE VIEW vw_planning_sales_24h AS
SELECT f.*
FROM fact_sales AS f
WHERE NOT EXISTS (
    SELECT 1
    FROM rapid_reversal_exclusions AS e
    WHERE e.source_row_id = f.source_row_id
);


SELECT
    COUNT(*) AS sale_lines,
    SUM(quantity) AS total_units,
    SUM(sales_value_gbp) AS sales_value_gbp
FROM vw_planning_sales_24h;