USE retail_supply_chain;

CREATE TABLE dim_product (
    stock_code VARCHAR(30) PRIMARY KEY,
    product_description TEXT NOT NULL
);

INSERT INTO dim_product (
    stock_code,
    product_description
)
SELECT
    StockCode,
    TRIM(Description)
FROM (
    SELECT
        StockCode,
        Description,
        ROW_NUMBER() OVER (
            PARTITION BY StockCode
            ORDER BY InvoiceDate DESC, source_row_id DESC
        ) AS row_rank
    FROM stg_eligible_sales
) AS ranked_products
WHERE row_rank = 1;


SELECT COUNT(*) AS product_count
FROM dim_product;

SELECT COUNT(*) AS unmatched_sale_lines
FROM fact_sales AS f
LEFT JOIN dim_product AS p
    ON f.stock_code = p.stock_code
WHERE p.stock_code IS NULL;