import pandas as pd
import numpy as np
from tabulate import tabulate
from scipy import stats

df = pd.read_csv(
    r'A:\portfolio\03_customer_segmentation_marketing_analysis\data\raw\marketing_campaign.csv',
    sep='\t'
)

# -------------------------------------------------------
# БЛОК 1: Базова структура датасету
# -------------------------------------------------------
print("=" * 60)
print(f"РОЗМІР: {df.shape[0]} рядків, {df.shape[1]} колонок")
print("=" * 60)

# -------------------------------------------------------
# БЛОК 2: Пропущені значення
# -------------------------------------------------------
missing = df.isnull().sum().reset_index()
missing.columns = ['Колонка', 'Пропусків']
missing = missing[missing['Пропусків'] > 0]
print("\nПРОПУЩЕНІ ЗНАЧЕННЯ:")
print(tabulate(missing, headers='keys', tablefmt='pretty', showindex=False))

# -------------------------------------------------------
# БЛОК 3: Дублікати
# -------------------------------------------------------
print(f"\nДУБЛІКАТИ: {df.duplicated().sum()} рядків")

# -------------------------------------------------------
# БЛОК 4: Категоріальні колонки — унікальні значення
# -------------------------------------------------------
cat_cols = df.select_dtypes(include='object').columns.tolist()
for col in cat_cols:
    vals = df[col].value_counts().reset_index()
    vals.columns = [col, 'Кількість']
    print(f"\n  {col}:")
    print(tabulate(vals, headers='keys', tablefmt='pretty', showindex=False))

# -------------------------------------------------------
# БЛОК 5: Числові колонки — IQR викиди
# -------------------------------------------------------
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
        'Колонка': col,
        'Min': df[col].min(),
        'Max': df[col].max(),
        'Median': round(df[col].median(), 1),
        'Mean': round(df[col].mean(), 1),
        'Викидів IQR': outliers
    })

print("\nСТАТИСТИКА + IQR ВИКИДИ:")
print(tabulate(outlier_report, headers='keys', tablefmt='pretty', showindex=False))

# -------------------------------------------------------
# БЛОК 6: Колонки-константи
# -------------------------------------------------------
constant_cols = [col for col in df.columns if df[col].nunique() == 1]
print(f"\nКОЛОНКИ-КОНСТАНТИ: {constant_cols}")

# -------------------------------------------------------
# БЛОК 7: Бізнес-валідація полів
# Перевіряємо логічну коректність ключових бізнес-полів
# -------------------------------------------------------
print("\n" + "=" * 60)
print("БІЗНЕС-ВАЛІДАЦІЯ")
print("=" * 60)

current_year = 2026

# Вік: рядки де вік від'ємний або > 100 років
age_issues = df[(current_year - df['Year_Birth'] < 0) |
                (current_year - df['Year_Birth'] > 100)]
print(f"\nВік — аномальні записи (від'ємний або >100 років): {len(age_issues)}")
if len(age_issues) > 0:
    print(tabulate(
        age_issues[['ID', 'Year_Birth']],
        headers='keys', tablefmt='pretty', showindex=False
    ))

# Дохід: нульовий або аномально великий (> 200k)
income_issues = df[(df['Income'] == 0) | (df['Income'] > 200000)]
print(f"\nДохід — аномальні записи (0 або >200k): {len(income_issues)}")
if len(income_issues) > 0:
    print(tabulate(
        income_issues[['ID', 'Income']].dropna(),
        headers='keys', tablefmt='pretty', showindex=False
    ))

# Дати: конвертуємо і перевіряємо чи не в майбутньому
df['Dt_Customer'] = pd.to_datetime(df['Dt_Customer'], dayfirst=True)
future_dates = df[df['Dt_Customer'] > pd.Timestamp('today')]
print(f"\nДати — записи в майбутньому: {len(future_dates)}")

# Мінімальна і максимальна дата реєстрації
print(f"Діапазон дат реєстрації: {df['Dt_Customer'].min().date()} → {df['Dt_Customer'].max().date()}")

# -------------------------------------------------------
# БЛОК 8: Z-score викиди (глобальні статистичні аномалії)
# Порогове значення |z| > 3 — стандарт у маркетинговій аналітиці
# Доповнює IQR: IQR ловить локальні викиди,
# Z-score — глобальні відхилення від середнього
# -------------------------------------------------------
print("\n" + "=" * 60)
print("Z-SCORE ВИКИДИ (|z| > 3)")
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
        'Колонка': col,
        'Викидів Z>3': n_outliers,
        'Max Z-score': max_z
    })

print(tabulate(zscore_report, headers='keys', tablefmt='pretty', showindex=False))

# -------------------------------------------------------
# БЛОК 9: Correlation sanity check
# Перевіряємо логічні зв'язки між ключовими бізнес-полями
# Дохід повинен корелювати з витратами і кількістю покупок
# Якщо кореляція слабка — це сигнал про проблеми в даних
# -------------------------------------------------------
print("\n" + "=" * 60)
print("КОРЕЛЯЦІЯ — SANITY CHECK")
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
        'Сильна ✅' if abs(corr) > 0.6
        else 'Середня ⚠️' if abs(corr) > 0.3
        else 'Слабка ❌'
    )
    corr_report.append({
        'Пара': f'{col1} ↔ {col2}',
        'Кореляція': round(corr, 3),
        'Оцінка': interpretation
    })

print(tabulate(corr_report, headers='keys', tablefmt='pretty', showindex=False))

# -------------------------------------------------------
# БЛОК 10: Memory optimization
# Зменшуємо використання пам'яті для ефективної роботи
# в Power BI та Python. object→category економить ~50%,
# int64→int32 та float64→float32 економлять ~50% на числах
# -------------------------------------------------------
print("\n" + "=" * 60)
print("ОПТИМІЗАЦІЯ ПАМ'ЯТІ")
print("=" * 60)

mem_before = df.memory_usage(deep=True).sum() / 1024 / 1024

for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].astype('category')

for col in df.select_dtypes(include='int64').columns:
    df[col] = df[col].astype('int32')

for col in df.select_dtypes(include='float64').columns:
    df[col] = df[col].astype('float32')

mem_after = df.memory_usage(deep=True).sum() / 1024 / 1024

# -------------------------------------------------------
# БЛОК 11: Профіль аномального клієнта Income = 666,666
# Дивимось весь рядок щоб зрозуміти чи це реальний клієнт
# -------------------------------------------------------
print("\n" + "=" * 60)
print("АНОМАЛЬНИЙ КЛІЄНТ — Income 666,666")
print("=" * 60)
print(df[df['Income'] == 666666].T.to_string())

# -------------------------------------------------------
# БЛОК 12: Медіани доходу по групах Education
# Це підтверджує логіку заповнення nulls —
# різні групи освіти мають суттєво різний дохід
# тому загальна медіана була б неточною
# -------------------------------------------------------
print("\n" + "=" * 60)
print("МЕДІАНИ ДОХОДУ ПО ГРУПАХ EDUCATION")
print("=" * 60)
medians = df.groupby('Education')['Income'].agg([
    ('Медіана', 'median'),
    ('Середнє', 'mean'),
    ('Мін', 'min'),
    ('Макс', 'max'),
    ('Кількість', 'count')
]).round(0).reset_index()
print(tabulate(medians, headers='keys', tablefmt='pretty', showindex=False))

print("\nЗавершено")