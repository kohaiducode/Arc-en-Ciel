import pandas as pd
import json

file_path = "C:/Users/81704/Desktop/Code/Sites/Arc-en-Ciel-v2/Contenu ancien site/Données ancien site et plateformes.xlsx"

# Read all sheets
xls = pd.ExcelFile(file_path)
data = {}
for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name)
    # convert dataframe to dict, handling NaNs
    data[sheet_name] = df.fillna("").to_dict(orient="records")

# Write to json
with open("C:/Users/81704/Desktop/Code/Sites/Arc-en-Ciel-v2/excel_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Excel data successfully written to excel_data.json")
