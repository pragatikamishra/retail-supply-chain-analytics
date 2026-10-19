from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[1]
file_path = project_root / "data" / "raw" / "Online Retail.xlsx"

df = pd.read_excel(file_path)

print("\n--- Rows and columns ---")
print(df.shape)

print("\n--- First five rows ---")
print(df.head().to_string())

print("\n--- Column types and non-null counts ---")
df.info()

print("\n--- Missing values per column ---")
print(df.isna().sum())

print("\n--- Exact duplicate rows ---")
print(df.duplicated().sum())

print("\n--- Invoice date range ---")
print(df["InvoiceDate"].min(), "to", df["InvoiceDate"].max())


print("\n--- Quantity checks ---")
print("Negative quantities:", (df["Quantity"] < 0).sum())
print("Zero quantities:", (df["Quantity"] == 0).sum())

print("\n--- Price checks ---")
print("Negative prices:", (df["UnitPrice"] < 0).sum())
print("Zero prices:", (df["UnitPrice"] == 0).sum())

# Invoice numbers beginning with C identify cancellations.
cancellation_mask = (
    df["InvoiceNo"]
    .astype("string")
    .str.strip()
    .str.upper()
    .str.startswith("C", na=False)
)

print("\n--- Cancellation and quantity breakdown ---")
print(
    pd.crosstab(
        cancellation_mask.rename("Cancellation invoice"),
        (df["Quantity"] < 0).rename("Negative quantity")
    )
)

columns = [
    "InvoiceNo", "StockCode", "Description",
    "Quantity", "UnitPrice", "CustomerID"
]

print("\n--- Cancellation examples ---")
print(df.loc[cancellation_mask, columns].head(10).to_string(index=False))

print("\n--- Negative quantities without cancellation prefix ---")
print(
    df.loc[
        (df["Quantity"] < 0) & ~cancellation_mask,
        columns
    ].head(10).to_string(index=False)
)

print("\n--- Non-positive price examples ---")
print(
    df.loc[df["UnitPrice"] <= 0, columns]
    .head(10)
    .to_string(index=False)
)

print("\n--- Negative-price records ---")
print(
    df.loc[df["UnitPrice"] < 0]
    .to_string(index=False)
)