# Raw Data Inspection

## Source

UCI Online Retail
https://archive.ics.uci.edu/dataset/352/online+retail

## Structure

- File: Online Retail.xlsx
- Rows: 541,909
- Columns: 8
- Grain: one recorded product transaction line within an invoice
- Date range: 2010-12-01 08:26 to 2011-12-09 12:50
- Currency: GBP
- InvoiceNo is not unique at line level.
- No explicit transaction-line identifier is supplied.

## Initial quality findings

- Missing Description: 1,454 rows
- Missing CustomerID: 135,080 rows
- Repeated rows beyond the first occurrence: 5,268
- CustomerID imported as a floating-point column.
- December 2011 contains only part of the month.

## Decisions pending investigation

- How to handle repeated records.
- How to classify cancellations and negative quantities.
- How to handle zero or negative prices.
- How to preserve transactions without customer IDs.

## Raw data handling

The original Excel file remains unchanged.

## Transaction exceptions

- Negative-quantity lines: 10,624
- Zero-quantity lines: 0
- Cancellation-prefixed lines: 9,288; all have negative quantities.
- Negative-quantity lines without cancellation prefix: 1,336.
- Zero-price lines: 2,515.
- Negative-price lines: 2.
- Exception counts overlap and must not be added together.
- Some StockCodes represent non-product entries, such as D (Discount).

## Initial analytical approach

- Preserve all raw records.
- Classify sales, cancellations, and exceptions before filtering.
- Retain missing-customer records for product-level analysis.
- Investigate duplicate candidates before removing them.
- Treat positive product sales as a proxy for demand.
- Do not assume cancellation dates match original sale dates.
- 

## Negative-price investigation

- Two records have StockCode B and description "Adjust bad debt".
- Each has Quantity 1 and UnitPrice -11,062.06 GBP.
- Invoice numbers and timestamps differ.
- Classification: accounting adjustment.
- Exclude from product-demand calculations; preserve for audit.


Exact repeated rows are excluded after the first occurrence as a project assumption. All source rows remain traceable. Because no transaction-line key exists, legitimate repeated lines cannot be ruled out.


The policy excludes  **5,221 repeated sale lines** , reducing units by **15,716** and sales value by  **£24,213.74** .
