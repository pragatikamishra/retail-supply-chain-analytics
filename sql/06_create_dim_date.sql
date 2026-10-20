USE retail_supply_chain;

CREATE TABLE dim_date (
    calendar_date DATE PRIMARY KEY,
    calendar_year SMALLINT NOT NULL,
    month_number TINYINT NOT NULL,
    year_month_label CHAR(7) NOT NULL,
    day_of_month TINYINT NOT NULL
);

INSERT INTO dim_date (
    calendar_date,
    calendar_year,
    month_number,
    year_month_label,
    day_of_month
)
WITH RECURSIVE date_series AS (
    SELECT MIN(sales_date) AS calendar_date
    FROM fact_sales

    UNION ALL

    SELECT DATE_ADD(calendar_date, INTERVAL 1 DAY)
    FROM date_series
    WHERE calendar_date < (
        SELECT MAX(sales_date)
        FROM fact_sales
    )
)
SELECT
    calendar_date,
    YEAR(calendar_date),
    MONTH(calendar_date),
    DATE_FORMAT(calendar_date, '%Y-%m'),
    DAY(calendar_date)
FROM date_series;



SELECT
    COUNT(*) AS calendar_days,
    MIN(calendar_date) AS first_date,
    MAX(calendar_date) AS last_date
FROM dim_date;

SELECT COUNT(*) AS unmatched_sale_lines
FROM fact_sales AS f
LEFT JOIN dim_date AS d
    ON f.sales_date = d.calendar_date
WHERE d.calendar_date IS NULL;