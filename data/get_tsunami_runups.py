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
    "itemsPerPage": 3083,
    #"sourceMaxCauseCode": 1,
    #"doubtful": "n"
}

records = []
for i in range(1,169):
    response = get_json_response('https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/runups', {"page":i})
    records += response['items']

print()
pprint(records)
print()

all_keys = set()
for record in records:
    all_keys.update(record.keys())

all_keys = sorted(all_keys)

with open('output_tsunami_runups.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=all_keys)
    writer.writeheader()
    writer.writerows(records)

print("✅ CSV file 'output.csv' written with dynamic columns.")
