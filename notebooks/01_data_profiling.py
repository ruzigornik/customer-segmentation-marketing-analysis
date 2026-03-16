import pandas as pd
import numpy as np
from tabulate import tabulate
from scipy import stats

df = pd.read_csv(
    r'A:\portfolio\03_customer_segmentation_marketing_analysis\data\raw\marketing_campaign.csv',
    sep='\t'
)

# Basic structure
print("=" * 60)
print(f"SIZE: {df.shape[0]} rows, {df.shape[1]} columns")
print("=" * 60)

# Missing values
missing = df.isnull().sum().reset_index()
missing.columns = ['Column', 'Missing']
missing = missing[missing['Missing'] > 0]
print("\nMISSING VALUES:")
print(tabulate(missing, headers='keys', tablefmt='pretty', showindex=False))

# Duplicates
print(f"\nDUPLICATES: {df.duplicated().sum()} rows")

# Categorical columns
cat_cols = df.select_dtypes(include='object').columns.tolist()
for col in cat_cols:
    vals = df[col].value_counts().reset_index()
    vals.columns = [col, 'Count']
    print(f"\n  {col}:")
    print(tabulate(vals, headers='keys', tablefmt='pretty', showindex=False))

# Numeric columns — IQR outliers
num_cols = df.select_dtypes(include=np.number).columns.tolist()
outlier_report = []
for col in num_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)][col].count()
    outlier_report.append({
        'Column': col,
        'Min': df[col].min(),
        'Max': df[col].max(),
        'Median': round(df[col].median(), 1),
        'Mean': round(df[col].mean(), 1),
        'IQR Outliers': outliers
    })

print("\nSTATISTICS + IQR OUTLIERS:")
print(tabulate(outlier_report, headers='keys', tablefmt='pretty', showindex=False))

# Constant columns
constant_cols = [col for col in df.columns if df[col].nunique() == 1]
print(f"\nCONSTANT COLUMNS: {constant_cols}")

# Business validation
print("\n" + "=" * 60)
print("BUSINESS VALIDATION")
print("=" * 60)

current_year = 2026
age_issues = df[(current_year - df['Year_Birth'] < 0) |
                (current_year - df['Year_Birth'] > 100)]
print(f"\nAge — anomalous records: {len(age_issues)}")

income_issues = df[(df['Income'] == 0) | (df['Income'] > 200000)]
print(f"\nIncome — anomalous records (0 or >200k): {len(income_issues)}")

df['Dt_Customer'] = pd.to_datetime(df['Dt_Customer'], dayfirst=True)
print(f"Registration date range: {df['Dt_Customer'].min().date()} → {df['Dt_Customer'].max().date()}")

# Z-score outliers (|z| > 3 — standard for marketing analytics)
print("\n" + "=" * 60)
print("Z-SCORE OUTLIERS (|z| > 3)")
print("=" * 60)

key_cols = ['Income', 'MntWines', 'MntMeatProducts',
            'MntFruits', 'MntFishProducts', 'MntSweetProducts',
            'MntGoldProds']

zscore_report = []
for col in key_cols:
    col_clean = df[col].dropna()
    z_scores = np.abs(stats.zscore(col_clean))
    n_outliers = (z_scores > 3).sum()
    max_z = round(z_scores.max(), 2)
    zscore_report.append({
        'Column': col,
        'Z>3 Outliers': n_outliers,
        'Max Z-score': max_z
    })

print(tabulate(zscore_report, headers='keys', tablefmt='pretty', showindex=False))

# Correlation sanity check
print("\n" + "=" * 60)
print("CORRELATION — SANITY CHECK")
print("=" * 60)

df['Total_Spending'] = (df['MntWines'] + df['MntFruits'] +
                        df['MntMeatProducts'] + df['MntFishProducts'] +
                        df['MntSweetProducts'] + df['MntGoldProds'])

df['Total_Purchases'] = (df['NumWebPurchases'] +
                         df['NumCatalogPurchases'] +
                         df['NumStorePurchases'])

corr_pairs = [
    ('Income', 'Total_Spending'),
    ('Income', 'Total_Purchases'),
    ('Total_Spending', 'Total_Purchases')
]

corr_report = []
for col1, col2 in corr_pairs:
    corr = df[[col1, col2]].dropna().corr().iloc[0, 1]
    interpretation = (
        'Strong' if abs(corr) > 0.6
        else 'Moderate' if abs(corr) > 0.3
        else 'Weak'
    )
    corr_report.append({
        'Pair': f'{col1} ↔ {col2}',
        'Correlation': round(corr, 3),
        'Assessment': interpretation
    })

print(tabulate(corr_report, headers='keys', tablefmt='pretty', showindex=False))

# Memory optimization (object→category, int64→int32, float64→float32)
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

# Anomalous customer Income = 666,666
print("\n" + "=" * 60)
print("ANOMALOUS CUSTOMER — Income 666,666")
print("=" * 60)
print(df[df['Income'] == 666666].T.to_string())

# Income medians by Education (for nulls imputation)
print("\n" + "=" * 60)
print("INCOME MEDIANS BY EDUCATION GROUP")
print("=" * 60)
medians = df.groupby('Education')['Income'].agg([
    ('Median', 'median'),
    ('Mean', 'mean'),
    ('Min', 'min'),
    ('Max', 'max'),
    ('Count', 'count')
]).round(0).reset_index()
print(tabulate(medians, headers='keys', tablefmt='pretty', showindex=False))

print("\nCompleted")