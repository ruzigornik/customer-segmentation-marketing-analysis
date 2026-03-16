import pandas as pd
import numpy as np
from tabulate import tabulate

df = pd.read_csv(
    r'A:\portfolio\03_customer_segmentation_marketing_analysis\data\processed\marketing_campaign_clean.csv'
)

print(f"Loaded cleaned dataset: {df.shape[0]} rows, {df.shape[1]} columns")

# Demographic features
current_year = pd.Timestamp.now().year
df['Age'] = current_year - df['Year_Birth']

df['Dt_Customer'] = pd.to_datetime(df['Dt_Customer'], dayfirst=True)
df['Customer_Tenure'] = (pd.Timestamp.now() - df['Dt_Customer']).dt.days

print("Demographic features created: Age, Customer_Tenure")

# Children in household
df['Total_Children'] = df['Kidhome'] + df['Teenhome']

print("Created: Total_Children")

# Spending features
df['Total_Spending'] = (
    df['MntWines'] +
    df['MntFruits'] +
    df['MntMeatProducts'] +
    df['MntFishProducts'] +
    df['MntSweetProducts'] +
    df['MntGoldProds']
)

# Average monthly spending (data covers 2 years = 24 months)
df['Avg_Monthly_Spending'] = (df['Total_Spending'] / 24).round(2)

print("Created: Total_Spending, Avg_Monthly_Spending")

# Purchase channels
df['Total_Purchases'] = (
    df['NumWebPurchases'] +
    df['NumCatalogPurchases'] +
    df['NumStorePurchases']
)

# Preferred_Channel — where customer buys most
df['Preferred_Channel'] = df[['NumWebPurchases',
                               'NumCatalogPurchases',
                               'NumStorePurchases']].idxmax(axis=1)

# Remove prefix 'Num' and suffix 'Purchases' for readability
df['Preferred_Channel'] = df['Preferred_Channel'].str.replace('Num', '').str.replace('Purchases', '')

print("Created: Total_Purchases, Preferred_Channel")

# Average check per purchase
# Protection against division by 0
df['Spending_Per_Purchase'] = (
    df['Total_Spending'] / df['Total_Purchases'].replace(0, np.nan)
).round(2)

print("Created: Spending_Per_Purchase")

# Marketing campaigns
df['Total_Campaigns_Accepted'] = (
    df['AcceptedCmp1'] +
    df['AcceptedCmp2'] +
    df['AcceptedCmp3'] +
    df['AcceptedCmp4'] +
    df['AcceptedCmp5'] +
    df['Response']
)

# Campaign response rate percentage
df['Campaign_Engagement_Rate'] = (
    df['Total_Campaigns_Accepted'] / 6 * 100
).round(2)

print("Created: Total_Campaigns_Accepted, Campaign_Engagement_Rate")

# Final check of new columns
new_cols = [
    'Age', 'Customer_Tenure', 'Total_Children',
    'Total_Spending', 'Avg_Monthly_Spending',
    'Total_Purchases', 'Preferred_Channel',
    'Spending_Per_Purchase', 'Total_Campaigns_Accepted',
    'Campaign_Engagement_Rate'
]

print("\n" + "=" * 60)
print("NEW COLUMNS — STATISTICS")
print("=" * 60)

# Numeric new columns
num_stats = df[new_cols[:-1]].describe().round(2).T.reset_index()
num_stats.columns = ['Column', 'Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max']
print(tabulate(num_stats, headers='keys', tablefmt='pretty', showindex=False))

# Preferred_Channel distribution
print("\nDistribution — Preferred_Channel:")
channel = df['Preferred_Channel'].value_counts().reset_index()
channel.columns = ['Channel', 'Count']
print(tabulate(channel, headers='keys', tablefmt='pretty', showindex=False))

print(f"\nTotal columns after Feature Engineering: {df.shape[1]}")

# Save final file
df.to_csv(
    r'A:\portfolio\03_customer_segmentation_marketing_analysis\data\processed\marketing_campaign_features.csv',
    index=False
)
print("File saved: data/processed/marketing_campaign_features.csv")