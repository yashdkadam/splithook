# api_key = "7IZPFA87RC6GPMYT"

# import requests
# from pprint import pprint

# url = "https://www.alphavantage.co/query"
# params = {
#     "function": "SYMBOL_SEARCH",
#     "keywords": "T",  # Replace with stock symbol
#     "apikey": "7IZPFA87RC6GPMYT"
# }
# response = requests.get(url, params=params)
# data = response.json()

# # Filter for BSE and NSE exchanges only
# filtered_data = [
#     entry for entry in data.get("bestMatches", [])
#     if ("India" in entry.get("4. region")) and (entry.get("8. currency") == "INR")
# ]

# pprint(filtered_data)


# import requests
# from pprint import pprint
# url = "https://www.nseindia.com/api/search/autocomplete"
# params = {"q": "TC"}  # Replace "TCS" with the stock symbol you want to search
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# }
# response = requests.get(url, headers=headers, params=params)
# data = response.json()
# pprint(data)

import requests

def fetch_stock_list(query):
    # NSE search endpoint (Unofficial API)
    url = "https://www.nseindia.com/api/search/autocomplete"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    params = {"q": query}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        return [
            {"symbol": item["symbol"], "name": item["symbol_info"]}
            for item in data.get("symbols", [])
        ]
    else:
        print("Failed to fetch data from NSE:", response.status_code)
        return []

# Example usage
query = "op"  # Replace with dynamic input from the user
matching_stocks = fetch_stock_list(query)
for stock in matching_stocks:
    print(stock)
