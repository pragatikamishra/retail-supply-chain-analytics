USE retail_supply_chain;

CREATE TABLE stg_eligible_sales (
    source_row_id INT PRIMARY KEY,
    InvoiceNo VARCHAR(30),
    StockCode VARCHAR(30),
    Description TEXT,
    Quantity INT,
    InvoiceDate DATETIME,
    UnitPrice DECIMAL(18,6),
    CustomerID VARCHAR(30),
    Country VARCHAR(100),
    is_cancellation VARCHAR(5),
    is_bad_debt_adjustment VARCHAR(5),
    is_non_product VARCHAR(5),
    needs_product_review VARCHAR(5),
    is_candidate_sale VARCHAR(5),
    is_exact_duplicate VARCHAR(5),
    is_eligible_sale VARCHAR(5),
    validated_invoice_date DATETIME,
    has_invalid_date VARCHAR(5),
    is_outside_expected_period VARCHAR(5),
    invoice_date DATE,
    line_sales_gbp DECIMAL(18,2)
);


DESCRIBE stg_eligible_sales;

USE retail_supply_chain;

SELECT
    COUNT(*) AS sale_lines,
    SUM(Quantity) AS total_units,
    SUM(line_sales_gbp) AS sales_value_gbp
FROM stg_eligible_sales;