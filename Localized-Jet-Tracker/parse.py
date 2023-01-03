import json
import requests

DUMP1090_ENDPOINT = 'http://192.168.86.202:8080'

def get_flights():
    # Load the flight data from a local JSON file
    #with open('example.json', encoding='utf-8') as f:
    #    data = json.load(f)

    # Load the flight data from a dump1090 endpoint
    response = requests.get(f'{DUMP1090_ENDPOINT}/data.json')
    data = response.json()

    # Get only the flight names from the data records
    flights = map(lambda record: record['flight'].strip(), data)

    # Return a set of flights which are not empty
    return set(filter(lambda name: name, flights))

flights = get_flights()

print('Found flights:', flights)