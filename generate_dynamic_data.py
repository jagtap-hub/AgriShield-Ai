import pandas as pd
import numpy as np

np.random.seed(42)
n = 500

first_names = ["Ramesh", "Suresh", "Anil", "Vijay", "Priya", "Rahul", "Sunita", "Ganesh", "Mahesh", "Kavita", "Deepak", "Sachin", "Pooja", "Vikram", "Anita"]
last_names = ["Patil", "Deshmukh", "Kale", "Shinde", "Sharma", "Pawar", "Jadhav", "Kulkarni", "Chavan", "Gaikwad", "More", "Joshi", "Bhosale", "Rao", "Verma"]
crops = ["Soybean", "Sugarcane", "Cotton", "Wheat", "Rice", "Onion"]
irrigation = ["Rain-fed", "Drip System", "Sprinkler", "Canal"]
soil_types = ["Black cotton soil", "Red loamy", "Alluvial", "Sandy loam"]
repayment_histories = ["Always on time", "Mostly on time", "1 delayed payment", "Frequently delayed"]

farmer_ids = [f"FARM-{1001 + i}" for i in range(n)]
farmer_names = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(n)]
loan_amounts = np.random.choice([50000, 100000, 150000, 200000, 250000, 300000, 500000], n)
outstanding = [int(amt * np.random.uniform(0.2, 0.85)) for amt in loan_amounts]
repayment = np.random.choice(repayment_histories, n, p=[0.5, 0.3, 0.15, 0.05])

fin_scores = np.random.normal(650, 80, n).clip(300, 850).astype(int)
crop_types = np.random.choice(crops, n)
farm_sizes = np.round(np.random.uniform(1.5, 20.0, n), 1)
irrigation_types = np.random.choice(irrigation, n)
soil_list = np.random.choice(soil_types, n)

hist_yields = np.round(np.random.uniform(8.0, 18.0, n), 1)
prev_yields = np.round(hist_yields * np.random.uniform(0.75, 1.05, n), 1)

rainfall = np.random.normal(800, 180, n).clip(300, 1400)
temp = np.random.normal(27, 4, n).clip(15, 42)
soil_moisture = np.random.normal(60, 15, n).clip(20, 95)
health_idx = np.round(np.random.uniform(0.4, 0.95, n), 2)

# Yield calculation in tons
yield_tons = (
    0.8 * farm_sizes * 
    (1 - abs(rainfall - 800)/1000) * 
    (1 - abs(temp - 25)/30) * 
    (soil_moisture/100) * 
    health_idx
) + np.random.normal(0, 0.5, n)
yield_tons = np.round(np.clip(yield_tons, 0.5, None), 2)

df = pd.DataFrame({
    'Farmer_ID': farmer_ids,
    'Farmer_Name': farmer_names,
    'Loan_Amount': loan_amounts,
    'Outstanding_Loan': outstanding,
    'Loan_Repayment_History': repayment,
    'Financial_History_Score': fin_scores,
    'Crop_Type': crop_types,
    'Farm_Size_acres': farm_sizes,
    'Irrigation_Type': irrigation_types,
    'Soil_Type': soil_list,
    'Historical_Yield': hist_yields,
    'Previous_Yield': prev_yields,
    'Rainfall_mm': np.round(rainfall, 1),
    'Temperature_C': np.round(temp, 1),
    'Soil_Moisture': np.round(soil_moisture, 1),
    'Crop_Health_Index': health_idx,
    'Yield_tons': yield_tons
})

df.to_csv("crop_data.csv", index=False)
print("Updated crop_data.csv successfully with 500 dynamic records.")
