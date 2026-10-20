from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
raw_file = project_root / "data" / "raw" / "Online Retail.xlsx"

# Read the source without modifying it.
raw_df = pd.read_excel(raw_file)

# Create a separate working dataset.
df = raw_df.copy()

# Record the original Excel row number.
# Row 1 contains headers, so data starts at row 2.
df.insert(0, "source_row_id", range(2, len(df) + 2))

print("Raw rows:", len(raw_df))
print("Working rows:", len(df))

print(
    df[["source_row_id", "InvoiceNo", "StockCode"]]
    .head()
    .to_string(index=False)
)
# Standardize identifiers without changing the raw file.
for column in ["InvoiceNo", "StockCode"]:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
        .str.upper()
    )

# Preserve missing customer IDs while removing the decimal representation.
df["CustomerID"] = df["CustomerID"].astype("Int64").astype("string")

# Trim surrounding whitespace; preserve missing values.
for column in ["Description", "Country"]:
    df[column] = df[column].astype("string").str.strip()

print("\n--- Standardized identifiers ---")
print(
    df[["InvoiceNo", "StockCode", "CustomerID"]]
    .head()
    .to_string(index=False)
)

print("\nMissing customer IDs:", df["CustomerID"].isna().sum())
df["is_cancellation"] = df["InvoiceNo"].str.startswith("C", na=False)

df["is_bad_debt_adjustment"] = (
    df["StockCode"].eq("B")
    & df["Description"]
        .str.casefold()
        .eq("adjust bad debt")
        .fillna(False)
)

print("\n--- Transaction flags ---")
print("Cancellation lines:", df["is_cancellation"].sum())
print("Bad-debt adjustment lines:", df["is_bad_debt_adjustment"].sum())

print("\n--- Flagged examples ---")
print(
    df.loc[
        df["is_cancellation"] | df["is_bad_debt_adjustment"],
        [
            "source_row_id", "InvoiceNo", "StockCode",
            "Quantity", "UnitPrice",
            "is_cancellation", "is_bad_debt_adjustment"
        ]
    ].head(10).to_string(index=False)
)
print("\n--- All bad-debt adjustments ---")
print(
    df.loc[
        df["is_bad_debt_adjustment"],
        [
            "source_row_id", "InvoiceNo", "StockCode",
            "Description", "Quantity", "InvoiceDate", "UnitPrice"
        ]
    ].to_string(index=False)
)


# Review codes that don't begin with a digit.
# This is an inspection rule, not an exclusion rule.
review_mask = ~df["StockCode"].str.match(r"^\d", na=False)

print("\n--- Possible non-product codes ---")
print(
    df.loc[review_mask]
    .groupby(["StockCode", "Description"], dropna=False)
    .size()
    .reset_index(name="line_count")
    .sort_values(["StockCode", "line_count"], ascending=[True, False])
    .to_string(index=False)
)

non_product_codes = {
    "AMAZONFEE",
    "B",
    "BANK CHARGES",
    "C2",
    "CRUK",
    "D",
    "DOT",
    "POST",
}

df["is_non_product"] = (
    df["StockCode"].isin(non_product_codes)
    | df["StockCode"].str.startswith("GIFT_", na=False)
)

# DCGS codes have mixed or missing descriptions.
# Keep them for investigation rather than assuming their meaning.
df["needs_product_review"] = (
    df["StockCode"].isin({"M", "S", "PADS"})
    | df["StockCode"].str.startswith("DCGS", na=False)
)

print("\n--- Product classification checks ---")
print("Non-product lines:", df["is_non_product"].sum())
print("Product-review lines:", df["needs_product_review"].sum())

print(
    df.loc[
        df["is_non_product"] | df["needs_product_review"]
    ]
    .groupby(
        ["StockCode", "is_non_product", "needs_product_review"],
        dropna=False
    )
    .size()
    .reset_index(name="line_count")
    .to_string(index=False)
)

df["is_candidate_sale"] = (
    ~df["is_cancellation"]
    & ~df["is_non_product"]
    & ~df["needs_product_review"]
    & df["Quantity"].gt(0)
    & df["UnitPrice"].gt(0)
    & df["InvoiceDate"].notna()
    & df["InvoiceNo"].notna()
    & df["StockCode"].notna()
)

print("\n--- Candidate product sales ---")
print("Candidate lines:", df["is_candidate_sale"].sum())
print("Other lines:", (~df["is_candidate_sale"]).sum())

print(
    df.loc[
        df["is_candidate_sale"],
        ["InvoiceNo", "StockCode", "Quantity", "UnitPrice"]
    ].head().to_string(index=False)
)

print(
    "Candidates missing customer ID:",
    df.loc[df["is_candidate_sale"], "CustomerID"].isna().sum()
)

print(
    "Candidates missing description:",
    df.loc[df["is_candidate_sale"], "Description"].isna().sum()
)

# Compare the original eight columns.
# Exclude source_row_id, which is unique for every source row.
source_columns = raw_df.columns.tolist()

df["is_exact_duplicate"] = raw_df.duplicated(
    subset=source_columns,
    keep="first"
)

duplicate_group_mask = raw_df.duplicated(
    subset=source_columns,
    keep=False
)

print("\n--- Duplicate checks ---")
print("Repeated rows beyond first:", df["is_exact_duplicate"].sum())

print(
    "Candidate sales flagged as repeated:",
    (
        df["is_candidate_sale"]
        & df["is_exact_duplicate"]
    ).sum()
)

print("\n--- Example repeated records ---")
print(
    df.loc[
        duplicate_group_mask,
        ["source_row_id"] + source_columns
    ]
    .sort_values(
        ["InvoiceNo", "StockCode", "InvoiceDate", "source_row_id"]
    )
    .head(12)
    .to_string(index=False)
)
# Analytical eligibility under our exact-duplicate policy.
df["is_eligible_sale"] = (
    df["is_candidate_sale"]
    & ~df["is_exact_duplicate"]
)

candidate_sales = df.loc[df["is_candidate_sale"]]
eligible_sales = df.loc[df["is_eligible_sale"]]

print("\n--- Duplicate-policy impact ---")
print("Candidate sale lines:", len(candidate_sales))
print("Eligible sale lines:", len(eligible_sales))
print("Excluded repeated sale lines:",
      len(candidate_sales) - len(eligible_sales))

units_before = candidate_sales["Quantity"].sum()
units_after = eligible_sales["Quantity"].sum()

value_before = (
    candidate_sales["Quantity"] * candidate_sales["UnitPrice"]
).sum()

value_after = (
    eligible_sales["Quantity"] * eligible_sales["UnitPrice"]
).sum()

print("Units before:", units_before)
print("Units after:", units_after)
print("Sales value before (GBP):", round(value_before, 2))
print("Sales value after (GBP):", round(value_after, 2))

# Preserve the source value; validate in a separate column.
df["validated_invoice_date"] = pd.to_datetime(
    df["InvoiceDate"],
    errors="coerce"
)

df["has_invalid_date"] = df["validated_invoice_date"].isna()

# Expected coverage established during Phase 1.
df["is_outside_expected_period"] = (
    df["validated_invoice_date"].notna()
    & (
        (df["validated_invoice_date"] < "2010-12-01")
        | (df["validated_invoice_date"] >= "2011-12-10")
    )
)

print("\n--- Date validation ---")
print("Invalid or missing dates:", df["has_invalid_date"].sum())
print("Dates outside expected period:",
      df["is_outside_expected_period"].sum())

print(
    "Eligible sale lines with date issues:",
    (
        df["is_eligible_sale"]
        & (
            df["has_invalid_date"]
            | df["is_outside_expected_period"]
        )
    ).sum()
)

print(
    "Validated date range:",
    df["validated_invoice_date"].min(),
    "to",
    df["validated_invoice_date"].max()
)

# Include validated dates in the final eligibility rule.
df["is_eligible_sale"] = (
    df["is_candidate_sale"]
    & ~df["is_exact_duplicate"]
    & ~df["has_invalid_date"]
    & ~df["is_outside_expected_period"]
)

eligible_sales = df.loc[df["is_eligible_sale"]].copy()

# Derived fields for daily SKU analysis.
eligible_sales["invoice_date"] = (
    eligible_sales["validated_invoice_date"].dt.date
)

eligible_sales["line_sales_gbp"] = (
    eligible_sales["Quantity"] * eligible_sales["UnitPrice"]
).round(2)

# Stop the script if a required check fails.
assert len(df) == len(raw_df), "Source rows were lost"
assert df["source_row_id"].is_unique, "Source row IDs are not unique"
assert eligible_sales["Quantity"].gt(0).all(), "Non-positive quantity"
assert eligible_sales["UnitPrice"].gt(0).all(), "Non-positive price"
assert eligible_sales["validated_invoice_date"].notna().all(), "Invalid date"
assert not eligible_sales["is_cancellation"].any(), "Cancellation included"
assert not eligible_sales["is_non_product"].any(), "Non-product included"
assert not eligible_sales["needs_product_review"].any(), "Review line included"
assert not eligible_sales["is_exact_duplicate"].any(), "Repeated line included"

print("\n--- Pre-export validation ---")
print("Checks passed")
print("Eligible sale lines:", len(eligible_sales))
print("Eligible units:", eligible_sales["Quantity"].sum())
print(
    "Eligible sales value (GBP):",
    round(eligible_sales["line_sales_gbp"].sum(), 2)
)

cleaned_folder = project_root / "data" / "cleaned"
cleaned_folder.mkdir(parents=True, exist_ok=True)

sales_file = cleaned_folder / "eligible_sales.csv"
audit_file = cleaned_folder / "transactions_audit.csv"

eligible_sales.to_csv(
    sales_file,
    index=False,
    encoding="utf-8"
)

df.to_csv(
    audit_file,
    index=False,
    encoding="utf-8"
)

# Check that the saved files contain the expected number of records.
sales_rows = len(pd.read_csv(sales_file, usecols=["source_row_id"]))
audit_rows = len(pd.read_csv(audit_file, usecols=["source_row_id"]))

assert sales_rows == len(eligible_sales), "Sales export count mismatch"
assert audit_rows == len(df), "Audit export count mismatch"

print("\n--- Export results ---")
print(f"Eligible sales: {sales_rows:,} rows")
print(f"Transaction audit: {audit_rows:,} rows")
print(f"Saved to: {cleaned_folder}")


cancellation_candidates = df.loc[
    df["is_cancellation"]
    & ~df["is_non_product"]
    & ~df["needs_product_review"]
    & ~df["is_exact_duplicate"]
    & ~df["has_invalid_date"]
    & ~df["is_outside_expected_period"]
    & df["Quantity"].lt(0)
    & df["UnitPrice"].gt(0)
].copy()

print("\n--- Product cancellation candidates ---")
print("Cancellation lines:", len(cancellation_candidates))
print(
    "With customer ID:",
    cancellation_candidates["CustomerID"].notna().sum()
)
print(
    "Missing customer ID:",
    cancellation_candidates["CustomerID"].isna().sum()
)


sales_for_matching = eligible_sales.loc[
    eligible_sales["CustomerID"].notna(),
    [
        "source_row_id", "CustomerID", "StockCode",
        "UnitPrice", "Quantity", "validated_invoice_date"
    ]
].copy()

cancellations_for_matching = cancellation_candidates.loc[
    cancellation_candidates["CustomerID"].notna(),
    [
        "source_row_id", "CustomerID", "StockCode",
        "UnitPrice", "Quantity", "validated_invoice_date"
    ]
].copy()

# Use the same positive quantity for comparison.
cancellations_for_matching["Quantity"] = (
    -cancellations_for_matching["Quantity"]
)

potential_pairs = cancellations_for_matching.merge(
    sales_for_matching,
    on=["CustomerID", "StockCode", "UnitPrice", "Quantity"],
    suffixes=("_cancel", "_sale"),
    how="inner"
)

# Only consider sales recorded before the cancellation.
potential_pairs = potential_pairs.loc[
    potential_pairs["validated_invoice_date_sale"]
    < potential_pairs["validated_invoice_date_cancel"]
].copy()

match_counts = potential_pairs.groupby(
    "source_row_id_cancel"
).size()

cancellation_match_review = cancellations_for_matching[
    ["source_row_id"]
].copy()

cancellation_match_review["candidate_sale_count"] = (
    cancellation_match_review["source_row_id"]
    .map(match_counts)
    .fillna(0)
    .astype(int)
)

print("\n--- Potential cancellation matches ---")
print(
    cancellation_match_review["candidate_sale_count"]
    .value_counts()
    .sort_index()
    .rename_axis("candidate_sale_count")
    .to_string(name="cancellation_lines")
)

# A sale appearing against several cancellations also needs review.
sale_match_counts = potential_pairs.groupby(
    "source_row_id_sale"
).size()

print(
    "\nSales linked to multiple cancellation candidates:",
    sale_match_counts.gt(1).sum()
)


potential_pairs["sale_candidates_for_cancel"] = (
    potential_pairs.groupby("source_row_id_cancel")[
        "source_row_id_sale"
    ].transform("size")
)

potential_pairs["cancel_candidates_for_sale"] = (
    potential_pairs.groupby("source_row_id_sale")[
        "source_row_id_cancel"
    ].transform("size")
)

unique_pairs = potential_pairs.loc[
    potential_pairs["sale_candidates_for_cancel"].eq(1)
    & potential_pairs["cancel_candidates_for_sale"].eq(1)
].copy()

unique_pairs["hours_to_cancellation"] = (
    unique_pairs["validated_invoice_date_cancel"]
    - unique_pairs["validated_invoice_date_sale"]
).dt.total_seconds() / 3600

print("\n--- Unique inferred cancellation pairs ---")
print("Pairs:", len(unique_pairs))

print("\nTime to cancellation, in hours:")
print(unique_pairs["hours_to_cancellation"].describe())

print("\nPreviously investigated SKUs:")
print(
    unique_pairs.loc[
        unique_pairs["StockCode"].isin(["23843", "23166"]),
        [
            "StockCode",
            "source_row_id_sale",
            "source_row_id_cancel",
            "Quantity",
            "hours_to_cancellation"
        ]
    ].to_string(index=False)
)


rapid_reversal_pairs = unique_pairs.loc[
    unique_pairs["hours_to_cancellation"].le(24)
].copy()

reversed_sale_ids = rapid_reversal_pairs["source_row_id_sale"]

planning_sales = eligible_sales.loc[
    ~eligible_sales["source_row_id"].isin(reversed_sale_ids)
].copy()

print("\n--- Rapid-reversal scenario ---")
print("Inferred pairs within 24 hours:", len(rapid_reversal_pairs))
print("Gross eligible sale lines:", len(eligible_sales))
print("Planning sale lines:", len(planning_sales))

print(
    "Units excluded:",
    eligible_sales["Quantity"].sum()
    - planning_sales["Quantity"].sum()
)

print(
    "Sales value excluded (GBP):",
    round(
        eligible_sales["line_sales_gbp"].sum()
        - planning_sales["line_sales_gbp"].sum(),
        2
    )
)

# Validate the matching before exporting.
assert rapid_reversal_pairs["source_row_id_sale"].is_unique
assert rapid_reversal_pairs["source_row_id_cancel"].is_unique

assert (
    len(eligible_sales) - len(planning_sales)
    == len(rapid_reversal_pairs)
), "Excluded sale count does not match pair count"

assert (
    eligible_sales["Quantity"].sum()
    - planning_sales["Quantity"].sum()
    == rapid_reversal_pairs["Quantity"].sum()
), "Excluded quantities do not reconcile"

planning_file = cleaned_folder / "planning_sales_24h.csv"
pairs_file = cleaned_folder / "rapid_reversal_pairs_24h.csv"

planning_sales.to_csv(planning_file, index=False, encoding="utf-8")
rapid_reversal_pairs.to_csv(pairs_file, index=False, encoding="utf-8")

print("\n--- Planning exports ---")
print("Planning sale lines:", len(planning_sales))
print("Planning units:", planning_sales["Quantity"].sum())
print(
    "Planning sales value (GBP):",
    round(planning_sales["line_sales_gbp"].sum(), 2)
)
print("Matching evidence pairs:", len(rapid_reversal_pairs))

reversal_ids = rapid_reversal_pairs[
    ["source_row_id_sale"]
].rename(columns={"source_row_id_sale": "source_row_id"})

assert len(reversal_ids) == 439
assert reversal_ids["source_row_id"].is_unique

reversal_ids.to_csv(
    cleaned_folder / "rapid_reversal_sale_ids.csv",
    index=False,
    encoding="utf-8"
)

print("Exported reversal sale IDs:", len(reversal_ids))

reversal_ids["exclusion_reason"] = "inferred_rapid_reversal_24h"

reversal_ids.to_csv(
    cleaned_folder / "rapid_reversal_sale_ids.csv",
    index=False,
    encoding="utf-8"
)

print("Exported reversal sale IDs:", len(reversal_ids))