USE retail_supply_chain;

SELECT
    s.stock_code,
    p.product_description,
    SUM(s.units_sold) AS total_units,
    SUM(s.sales_value_gbp) AS total_sales_gbp,
    COUNT(*) AS days_with_sales
FROM daily_sku_sales AS s
JOIN dim_product AS p
    ON s.stock_code = p.stock_code
GROUP BY
    s.stock_code,
    p.product_description
ORDER BY total_units DESC, s.stock_code
LIMIT 10;

SELECT
    invoice_no,
    customer_id,
    invoice_datetime,
    quantity,
    unit_price,
    sales_value_gbp
FROM fact_sales
WHERE stock_code = '23166'
ORDER BY quantity DESC
LIMIT 10;