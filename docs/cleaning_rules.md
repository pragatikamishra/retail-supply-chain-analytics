# Data Cleaning Rules

## Source and traceability

- Source: UCI Online Retail, downloaded as an unchanged Excel file.
- Input: 541,909 transaction lines.
- source_row_id records the original Excel row number.
- The audit export preserves every source row with classification flags.

## Standardization

- InvoiceNo and StockCode: converted to text, trimmed, and uppercased.
- CustomerID: converted to text without decimal suffixes.
- Missing customer IDs remain missing.
- Description and Country: surrounding whitespace removed.

## Transaction classification

- Invoice numbers beginning with C are flagged as cancellations.
- Identified fees, postage, discounts, bad-debt adjustments,
  and gift vouchers are excluded from physical-product demand.
- Manual entries, samples, PADS, and DCGS-prefixed codes
  are held for product review.
- These are documented project rules, not confirmed source-system rules.

## Duplicate policy

- Compare the original eight source columns.
- Exclude exact repeats after their first occurrence from analysis.
- Preserve all occurrences in the audit export.
- Without a transaction-line key, legitimate repeated lines
  cannot be ruled out.

## Eligible sales

A line must:

- Have positive quantity and unit price.
- Have an invoice number and stock code.
- Have a valid date within the inspected source period.
- Not be a cancellation, identified non-product, review record,
  or repeated occurrence.

Missing customer IDs do not disqualify product-level sales.

## Derived fields

- invoice_date: calendar date used for daily analysis.
- line_sales_gbp: quantity multiplied by unit price, rounded
  to two decimal places.

## Validation results

- Eligible sale lines: 522,504
- Eligible units: 5,561,280
- Eligible sales value: GBP 10,246,820.87
- Audit lines: 541,909
- Invalid dates: 0
- Dates outside expected coverage: 0

## Limitations

- Recorded sales are a demand proxy, not total customer demand.
- Eligible sales value excludes cancellations and other excluded
  records; it is not net company revenue or profit.
- Inventory balances and supplier lead times are not supplied.
- December 2011 is incomplete.

## Outputs

- data/cleaned/eligible_sales.csv
- data/cleaned/transactions_audit.csv


## Rapid-reversal planning scenario

Purpose:
Reduce the influence of apparent rapid transaction reversals
on product-demand analysis.

Matching conditions:

- Same known customer ID, stock code, unit price and quantity.
- Cancellation quantity is the exact opposite of sale quantity.
- Sale occurs before cancellation.
- Each cancellation has exactly one candidate sale.
- Each sale has exactly one candidate cancellation.
- Cancellation occurs within 24 hours of the sale.

The 24-hour threshold is a project assumption.
Matches are inferred, not confirmed original-invoice links.

Results:

- Inferred reversal pairs: 439
- Excluded units: 170,451
- Excluded sales value: GBP 276,957.94
- Remaining sale lines: 522,065
- Remaining units: 5,390,829
- Remaining sales value: GBP 9,969,862.93

Outputs:

- data/cleaned/planning_sales_24h.csv
- data/cleaned/rapid_reversal_pairs_24h.csv

Limitations:

- This is not a complete cancellation or returns reconciliation.
- Partial, ambiguous, missing-customer and longer-gap
  cancellations remain unresolved.
- Gross-sales outputs remain available for comparison.
- Historical forecast testing must avoid using cancellations
  that were not yet known at the forecast cutoff.
