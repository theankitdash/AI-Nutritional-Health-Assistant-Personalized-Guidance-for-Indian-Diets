import os
import requests
from dotenv import load_dotenv

# Load the API key from .env file
load_dotenv()
API_KEY = os.getenv("USDA_API_KEY")

# Base URLs
SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
DETAIL_URL = "https://api.nal.usda.gov/fdc/v1/food/"

# Function to search for foods by name
def search_foods(query, page_size=5):
    
    params = {
        "api_key": API_KEY,
        "query": query,
        "pageSize": page_size,
    }
    response = requests.get(SEARCH_URL, params=params)
    if response.status_code == 200:
        return response.json().get("foods", [])
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []

# Function to get detailed nutritional data for a food item by its FDC ID
def get_food_details(fdc_id):
    
    params = {"api_key": API_KEY}
    response = requests.get(f"{DETAIL_URL}{fdc_id}", params=params)
    
    if response.status_code == 200:
        food_details = response.json()
       
        print(food_details)  # Data returned by the API
    else:
        print(f"Error {response.status_code}: {response.text}")


def main():
    # Prompt user for food search query
    food_query = input("Enter a food to search for: ")
    
    # Search for food items based on query
    results = search_foods(food_query)
    print(f"\nSearch Results for '{food_query}':")
    
    if results:
        # Automatically get details of the first result
        fdc_id = results[0]['fdcId']
        print(f"\nFetching details for '{results[0]['description']}' with FDC ID: {fdc_id}")
        get_food_details(fdc_id)
    else:
        print(f"No results found for '{food_query}'. Please try a different search.")

if __name__ == "__main__":
    main()
