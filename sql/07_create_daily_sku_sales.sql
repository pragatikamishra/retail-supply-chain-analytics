USE retail_supply_chain;

CREATE TABLE daily_sku_sales (
    sales_date DATE NOT NULL,
    stock_code VARCHAR(30) NOT NULL,
    units_sold BIGINT NOT NULL,
    sales_value_gbp DECIMAL(18,2) NOT NULL,
    invoice_count INT NOT NULL,

    PRIMARY KEY (sales_date, stock_code),

    FOREIGN KEY (sales_date)
        REFERENCES dim_date(calendar_date),

    FOREIGN KEY (stock_code)
        REFERENCES dim_product(stock_code)
);

INSERT INTO daily_sku_sales (
    sales_date,
    stock_code,
    units_sold,
    sales_value_gbp,
    invoice_count
)
SELECT
    sales_date,
    stock_code,
    SUM(quantity),
    SUM(sales_value_gbp),
    COUNT(DISTINCT invoice_no)
FROM fact_sales
GROUP BY sales_date, stock_code;

SELECT
    COUNT(*) AS daily_sku_rows,
    SUM(units_sold) AS total_units,
    SUM(sales_value_gbp) AS total_sales_gbp
FROM daily_sku_sales;