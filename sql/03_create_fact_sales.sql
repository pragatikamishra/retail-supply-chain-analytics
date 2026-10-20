USE retail_supply_chain;

CREATE TABLE fact_sales (
    source_row_id INT PRIMARY KEY,
    invoice_no VARCHAR(30) NOT NULL,
    stock_code VARCHAR(30) NOT NULL,
    customer_id VARCHAR(30),
    country VARCHAR(100),
    invoice_datetime DATETIME NOT NULL,
    sales_date DATE NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(18,6) NOT NULL,
    sales_value_gbp DECIMAL(18,2) NOT NULL,

    INDEX idx_sales_date_stock (sales_date, stock_code)
);

INSERT INTO fact_sales (
    source_row_id,
    invoice_no,
    stock_code,
    customer_id,
    country,
    invoice_datetime,
    sales_date,
    quantity,
    unit_price,
    sales_value_gbp
)
SELECT
    source_row_id,
    InvoiceNo,
    StockCode,
    NULLIF(TRIM(CustomerID), ''),
    Country,
    InvoiceDate,
    invoice_date,
    Quantity,
    UnitPrice,
    line_sales_gbp
FROM stg_eligible_sales;



SELECT
    COUNT(*) AS sale_lines,
    SUM(quantity) AS total_units,
    SUM(sales_value_gbp) AS sales_value_gbp
FROM fact_sales;