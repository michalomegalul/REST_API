import requests
import pandas as pd

product_id = pd.read_csv("./data.csv")["id"]
base_url = "http://localhost:5000/api/products"

for i in product_id:
    url = f"{base_url}/{i}/offers"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            print(response.json())
        except ValueError:
            print("Invalid JSON format")
    else:
        print(f"Error: {response.status_code} - {response.reason}")
