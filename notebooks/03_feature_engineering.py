import pandas as pd
import numpy as np
from tabulate import tabulate

df = pd.read_csv(
    r'A:\portfolio\03_customer_segmentation_marketing_analysis\data\processed\marketing_campaign_clean.csv'
)

print(f"Завантажено очищений датасет: {df.shape[0]} рядків, {df.shape[1]} колонок")

# -------------------------------------------------------
# БЛОК 1: Демографічні ознаки
# -------------------------------------------------------

# Вік клієнта — рахуємо відносно поточного року автоматично
current_year = pd.Timestamp.now().year
df['Age'] = current_year - df['Year_Birth']

# Стаж клієнта в днях — скільки днів з моменту реєстрації
df['Dt_Customer'] = pd.to_datetime(df['Dt_Customer'], dayfirst=True)
df['Customer_Tenure'] = (pd.Timestamp.now() - df['Dt_Customer']).dt.days

print("✅ Демографічні ознаки створено: Age, Customer_Tenure")

# -------------------------------------------------------
# БЛОК 2: Діти в домогосподарстві
# -------------------------------------------------------

# Загальна кількість дітей (малі + підлітки)
df['Total_Children'] = df['Kidhome'] + df['Teenhome']

print("✅ Створено: Total_Children")

# -------------------------------------------------------
# БЛОК 3: Витрати
# -------------------------------------------------------

# Загальні витрати по всіх категоріях товарів
df['Total_Spending'] = (
    df['MntWines'] +
    df['MntFruits'] +
    df['MntMeatProducts'] +
    df['MntFishProducts'] +
    df['MntSweetProducts'] +
    df['MntGoldProds']
)

# Середні витрати на місяць (дані за 2 роки = 24 місяці)
df['Avg_Monthly_Spending'] = (df['Total_Spending'] / 24).round(2)

print("✅ Створено: Total_Spending, Avg_Monthly_Spending")

# -------------------------------------------------------
# БЛОК 4: Канали покупок
# -------------------------------------------------------

# Загальна кількість покупок по всіх каналах
df['Total_Purchases'] = (
    df['NumWebPurchases'] +
    df['NumCatalogPurchases'] +
    df['NumStorePurchases']
)

# Preferred_Channel — де клієнт купує найбільше
df['Preferred_Channel'] = df[['NumWebPurchases',
                               'NumCatalogPurchases',
                               'NumStorePurchases']].idxmax(axis=1)

# Прибираємо префікс 'Num' і суфікс 'Purchases' для читабельності
df['Preferred_Channel'] = df['Preferred_Channel'].str.replace('Num', '').str.replace('Purchases', '')

print("✅ Створено: Total_Purchases, Preferred_Channel")

# -------------------------------------------------------
# БЛОК 5: Середній чек
# -------------------------------------------------------

# Скільки в середньому витрачає за одну покупку
# Захист від ділення на 0 — якщо покупок не було
df['Spending_Per_Purchase'] = (
    df['Total_Spending'] / df['Total_Purchases'].replace(0, np.nan)
).round(2)

print("✅ Створено: Spending_Per_Purchase")

# -------------------------------------------------------
# БЛОК 6: Маркетингові кампанії
# -------------------------------------------------------

# Загальна кількість прийнятих кампаній (з 6 можливих)
df['Total_Campaigns_Accepted'] = (
    df['AcceptedCmp1'] +
    df['AcceptedCmp2'] +
    df['AcceptedCmp3'] +
    df['AcceptedCmp4'] +
    df['AcceptedCmp5'] +
    df['Response']
)

# Відсоток відгуку на кампанії
df['Campaign_Engagement_Rate'] = (
    df['Total_Campaigns_Accepted'] / 6 * 100
).round(2)

print("✅ Створено: Total_Campaigns_Accepted, Campaign_Engagement_Rate")

# -------------------------------------------------------
# БЛОК 7: Фінальна перевірка нових колонок
# -------------------------------------------------------
new_cols = [
    'Age', 'Customer_Tenure', 'Total_Children',
    'Total_Spending', 'Avg_Monthly_Spending',
    'Total_Purchases', 'Preferred_Channel',
    'Spending_Per_Purchase', 'Total_Campaigns_Accepted',
    'Campaign_Engagement_Rate'
]

print("\n" + "=" * 60)
print("НОВІ КОЛОНКИ — СТАТИСТИКА")
print("=" * 60)

# Числові нові колонки
num_stats = df[new_cols[:-1]].describe().round(2).T.reset_index()
num_stats.columns = ['Колонка', 'Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max']
print(tabulate(num_stats, headers='keys', tablefmt='pretty', showindex=False))

# Preferred_Channel — розподіл
print("\nРОЗПОДІЛ — Preferred_Channel:")
channel = df['Preferred_Channel'].value_counts().reset_index()
channel.columns = ['Канал', 'Кількість']
print(tabulate(channel, headers='keys', tablefmt='pretty', showindex=False))

print(f"\nВсього колонок після Feature Engineering: {df.shape[1]}")

# -------------------------------------------------------
# БЛОК 8: Збереження фінального файлу
# -------------------------------------------------------
df.to_csv(
    r'A:\portfolio\03_customer_segmentation_marketing_analysis\data\processed\marketing_campaign_features.csv',
    index=False
)
print("✅ Файл збережено: data/processed/marketing_campaign_features.csv")