from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile
from io import BytesIO

project_root = Path(__file__).resolve().parents[1]
raw_folder = project_root / "data" / "raw"
raw_folder.mkdir(parents=True, exist_ok=True)

output_file = raw_folder / "Online Retail.xlsx"
url = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"

if output_file.exists():
    print(f"File already exists: {output_file}")
else:
    print("Downloading dataset...")

    with urlopen(url, timeout=120) as response:
        zip_bytes = response.read()

    with ZipFile(BytesIO(zip_bytes)) as archive:
        excel_bytes = archive.read("Online Retail.xlsx")

    output_file.write_bytes(excel_bytes)
    print(f"Saved: {output_file}")