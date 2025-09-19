import requests
import csv
from pprint import pprint

def get_json_response(url, params):
    """
    Access a URL with query parameters and return the JSON response.

    Args:
        url (str): The base URL to request.
        params (dict): Dictionary of query parameters.

    Returns:
        dict: JSON response from the URL.
    """
    response = requests.get(url, params=params)
    print(response.url)
    response.raise_for_status()
    return response.json()

params = {
    "itemsPerPage": 200,
    "sourceMaxCauseCode": 1,
    "doubtful": "n"
}

response = get_json_response('https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/runups', params)
records = response['items']

print()
pprint(records)
print()

# 🔍 Collect all unique keys from all records
all_keys = set()
for record in records:
    all_keys.update(record.keys())

# Convert to a sorted list (optional)
all_keys = sorted(all_keys)

# ✅ Use all_keys instead of records[0].keys()
with open('output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=all_keys)
    writer.writeheader()
    writer.writerows(records)

print("✅ CSV file 'output.csv' written with dynamic columns.")
