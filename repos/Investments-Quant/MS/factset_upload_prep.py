import pandas as pd
import os

# ── Input
file_path = r"C:\Users\shreya.lingam\OneDrive - Mediolanum International Funds\Desktop\MIA\MS Rotation\Fisher Approval Deck\MST FIIG Global Equity ACWI Style Upload.xlsx"

# ── Read
ext = os.path.splitext(file_path)[1].lower()
if ext == '.csv':
    df = pd.read_csv(file_path)
elif ext in ('.xlsx', '.xls'):
    df = pd.read_excel(file_path)
else:
    raise ValueError(f"Unsupported file type: {ext}")

# Normalise column names
df.columns = df.columns.str.strip().str.replace(' ', '_')

print(f"\nLoaded {len(df)} rows, columns: {list(df.columns)}")

# ── Group by ISIN and Date, sum Weight and Shares
grouped = df.groupby(['Security_Name', 'ISIN', 'Date'], as_index=False)[['Weight', 'Shares']].sum()
grouped = grouped.sort_values(['Date', 'Weight'], ascending=[True, False]).reset_index(drop=True)

print(f"Grouped into {len(grouped)} rows\n")
print(grouped.head(20))

# ── Output
out_dir = os.path.dirname(file_path)
out_path = os.path.join(out_dir, 'factset_upload_grouped_fisher_a8.xlsx')
grouped.to_excel(out_path, index=False)
print(f"\nSaved to: {out_path}")
