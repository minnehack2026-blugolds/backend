import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch

# Read CSV with semicolon delimiter
print("Loading universities from CSV...")
df = pd.read_csv(
    "scripts/universities.csv",
    sep=';',
    on_bad_lines='skip',
    encoding='utf-8',
    low_memory=False
)

print(f"Total universities loaded: {len(df)}")

# Filter for Minnesota
mn_universities = df[df['STATE'] == 'MN']
print(f"Found {len(mn_universities)} universities in Minnesota")

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="campus_marketplace",
    user="postgres",
    password="postgres",
    port="5431"
)

cursor = conn.cursor()

# First, clear existing data (optional - remove if you want to keep what's there)
cursor.execute("DELETE FROM universities")
print("Cleared existing data")

# Prepare values with coordinates - handle different data types
values = []
for _, row in mn_universities.iterrows():
    try:
        name = str(row['NAME']) if pd.notna(row['NAME']) else None
        lat = float(row['LATITUDE']) if pd.notna(row['LATITUDE']) else None
        lng = float(row['LONGITUDE']) if pd.notna(row['LONGITUDE']) else None
        
        if name and lat and lng:  # Only insert if all three exist
            values.append((name, lat, lng))
    except (ValueError, TypeError) as e:
        print(f"Skipping {row.get('NAME', 'unknown')}: {e}")
        continue

print(f"\nInserting {len(values)} Minnesota universities with valid coordinates...")

# Insert with coordinates
execute_batch(
    cursor,
    "INSERT INTO universities (name, latitude, longitude) VALUES (%s, %s, %s)",
    values,
    page_size=100
)

conn.commit()
cursor.close()
conn.close()

print("✓ Done! Minnesota universities seeded successfully.")
print(f"✓ Inserted {len(values)} universities with coordinates")
'''print("Loading universies from CSV....")
df = pd.read_csv("https://lehd.ces.census.gov/data/pseo/R2022Q4/all/pseo_all_institutions.csv")
 
 print(f"Total universities in dataset: {len(df)}")
print("Columns available:", df.columns.tolist())

# Filter to Minnesota (check the actual column name for state)
# Common column names: 'state', 'State', 'stabbr', etc.
mn_universities = df[df['stabbr'] == 'MN']  # Adjust column name as needed

print(f"Universities in Minnesota: {len(mn_universities)}")

 
 # connects to postgres database
conn = psycopg2.connect(
    host ="localhost",
    database = "campus_marketplace",
    user = "postgres",
    password = "postgres",
    port = "5431"
)

cursor = conn.cursor()

values = [
    (row['istmn'],)
    for _, row in mn_universities.iterrows()
]

print(f"Inserting {len(values)} universities...")


execute_batch(
    cursor,
    "insert into universities (name) (%s) on conflict (name) do nothing",
    values,
    page_size =100
)

conn.commit()
cursor.close()
conn.close()
print(done!)'''

