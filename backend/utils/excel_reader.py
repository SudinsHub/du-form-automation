import pandas as pd

# Load all sheets
all_sheets = pd.read_excel('Bills_Demo.xlsx', sheet_name="Examiners")
courses = all_sheets['Course']
# Print the first few rows of the Q1 data
print("--- Examiners Data ---")
for ind, crs in courses.items():
    print(f"course {ind+1}: {crs}")