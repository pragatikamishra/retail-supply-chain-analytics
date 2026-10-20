USE retail_supply_chain;

CREATE TABLE rapid_reversal_exclusions (
    source_row_id INT PRIMARY KEY,

    FOREIGN KEY (source_row_id)
        REFERENCES fact_sales(source_row_id)
);

ALTER TABLE rapid_reversal_exclusions
ADD COLUMN exclusion_reason VARCHAR(50);

SELECT COUNT(*) AS excluded_sale_lines
FROM rapid_reversal_exclusions;