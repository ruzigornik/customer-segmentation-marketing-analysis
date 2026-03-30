import pandas as pd
import numpy as np
from tabulate import tabulate

df = pd.read_csv(
    r'A:\portfolio\03_customer_segmentation_marketing_analysis\data\raw\marketing_campaign.csv',
    sep='\t'
)

print(f"Рядків до чистки: {df.shape[0]}")

# -------------------------------------------------------
# БЛОК 1: Видалення колонок-констант
# Z_CostContact і Z_Revenue — однакове значення для всіх
# -------------------------------------------------------
df = df.drop(columns=['Z_CostContact', 'Z_Revenue'])
print(f"✅ Видалено колонки-константи. Колонок залишилось: {df.shape[1]}")

# -------------------------------------------------------
# БЛОК 2: Видалення аномальних дат народження
# Клієнти старше 100 років — помилка введення даних
# -------------------------------------------------------
df = df[df['Year_Birth'] >= 1925]
print(f"✅ Видалено аномальний вік. Рядків залишилось: {df.shape[0]}")

# -------------------------------------------------------
# БЛОК 3: Видалення аномального доходу
# Income=666,666 але витрати лише $62 — явна помилка
# -------------------------------------------------------
df = df[df['Income'] != 666666]
print(f"✅ Видалено аномальний дохід. Рядків залишилось: {df.shape[0]}")

# -------------------------------------------------------
# БЛОК 4: Чистка Marital_Status
# Alone → Single (та сама категорія, різне написання)
# Absurd, YOLO → видаляємо (сміттєві записи)
# -------------------------------------------------------
df['Marital_Status'] = df['Marital_Status'].replace('Alone', 'Single')
df = df[~df['Marital_Status'].isin(['Absurd', 'YOLO'])]
print(f"✅ Почищено Marital_Status. Рядків залишилось: {df.shape[0]}")

# Перевіряємо результат
status_check = df['Marital_Status'].value_counts().reset_index()
status_check.columns = ['Marital_Status', 'Кількість']
print(tabulate(status_check, headers='keys', tablefmt='pretty', showindex=False))

# -------------------------------------------------------
# БЛОК 5: Заповнення пропусків Income
# Медіана по групі Education — чесніше ніж загальна медіана
# PhD і Basic мають суттєво різний рівень доходу
# -------------------------------------------------------
df['Income'] = df.groupby('Education')['Income'].transform(
    lambda x: x.fillna(x.median())
)
print(f"\n✅ Заповнено пропуски Income. Залишилось nulls: {df['Income'].isnull().sum()}")

# -------------------------------------------------------
# БЛОК 6: Фінальна перевірка
# -------------------------------------------------------
print("\n" + "=" * 60)
print("РЕЗУЛЬТАТ ЧИСТКИ")
print("=" * 60)
print(f"Рядків: {df.shape[0]} | Колонок: {df.shape[1]}")
print(f"Пропусків: {df.isnull().sum().sum()}")

# Скидаємо індекси після видалення рядків —
# прибираємо "діри" які утворились після чистки
df = df.reset_index(drop=True)

# -------------------------------------------------------
# БЛОК 7: Оптимізація пам'яті перед збереженням
# Зменшуємо розмір файлу для ефективної роботи в Power BI
# -------------------------------------------------------
mem_before = df.memory_usage(deep=True).sum() / 1024 / 1024

for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].astype('category')
for col in df.select_dtypes(include='int64').columns:
    df[col] = df[col].astype('int32')
for col in df.select_dtypes(include='float64').columns:
    df[col] = df[col].astype('float32')

df.to_csv(
    r'A:\portfolio\03_customer_segmentation_marketing_analysis\data\processed\marketing_campaign_clean.csv',
    index=False
)
print("\n✅ Файл збережено: data/processed/marketing_campaign_clean.csv")