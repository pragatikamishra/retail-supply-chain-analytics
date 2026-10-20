USE retail_supply_chain;

CREATE VIEW vw_daily_sku_planning_24h AS
SELECT
    sales_date,
    stock_code,
    SUM(quantity) AS units_sold,
    SUM(sales_value_gbp) AS sales_value_gbp,
    COUNT(DISTINCT invoice_no) AS invoice_count
FROM vw_planning_sales_24h
GROUP BY sales_date, stock_code;


SELECT
    COUNT(*) AS daily_sku_rows,
    SUM(units_sold) AS total_units,
    SUM(sales_value_gbp) AS total_sales_gbp
FROM vw_daily_sku_planning_24h;