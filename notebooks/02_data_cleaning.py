import pandas as pd
import numpy as np
from tabulate import tabulate

df = pd.read_csv(
    r'A:\portfolio\03_customer_segmentation_marketing_analysis\data\raw\marketing_campaign.csv',
    sep='\t'
)

print(f"Rows before cleaning: {df.shape[0]}")

# Remove constant columns (same value for all rows)
df = df.drop(columns=['Z_CostContact', 'Z_Revenue'])
print(f"Constant columns removed. Columns left: {df.shape[1]}")

# Remove anomalous birth years (customers older than 100 years — data entry error)
df = df[df['Year_Birth'] >= 1925]
print(f"Anomalous age removed. Rows left: {df.shape[0]}")

# Remove anomalous income (Income=$666k with only $62 spending — clear error)
df = df[df['Income'] != 666666]
print(f"Anomalous income removed. Rows left: {df.shape[0]}")

# Clean Marital_Status: Alone → Single, remove garbage categories
df['Marital_Status'] = df['Marital_Status'].replace('Alone', 'Single')
df = df[~df['Marital_Status'].isin(['Absurd', 'YOLO'])]
print(f"Marital_Status cleaned. Rows left: {df.shape[0]}")

status_check = df['Marital_Status'].value_counts().reset_index()
status_check.columns = ['Marital_Status', 'Count']
print(tabulate(status_check, headers='keys', tablefmt='pretty', showindex=False))

# Fill Income nulls with median by Education group
# Different education levels have significantly different income levels
df['Income'] = df.groupby('Education')['Income'].transform(
    lambda x: x.fillna(x.median())
)
print(f"\n Income nulls filled. Remaining nulls: {df['Income'].isnull().sum()}")

# Final check
print("\n" + "=" * 60)
print("CLEANING RESULT")
print("=" * 60)
print(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
print(f"Missing values: {df.isnull().sum().sum()}")

# Reset index after row deletions
df = df.reset_index(drop=True)

# Memory optimization before saving (reduces file size for Power BI)
print("\n" + "=" * 60)
print("MEMORY OPTIMIZATION")
print("=" * 60)

mem_before = df.memory_usage(deep=True).sum() / 1024 / 1024

for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].astype('category')
for col in df.select_dtypes(include='int64').columns:
    df[col] = df[col].astype('int32')
for col in df.select_dtypes(include='float64').columns:
    df[col] = df[col].astype('float32')

mem_after = df.memory_usage(deep=True).sum() / 1024 / 1024

df.to_csv(
    r'A:\portfolio\03_customer_segmentation_marketing_analysis\data\processed\marketing_campaign_clean.csv',
    index=False
)
print("\nFile saved: data/processed/marketing_campaign_clean.csv")