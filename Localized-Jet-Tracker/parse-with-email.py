import boto3
from botocore.exceptions import ClientError
import datetime
import json
import requests

# Create a new SES resource and specify the region
client = boto3.client('ses', region_name="us-west-2")
CHARSET = "UTF-8"
FLIGHTS_OF_INTEREST = ['FLY711']
DUMP1090_ENDPOINT = 'http://192.168.86.202:8080'

def get_flights():
  # Load the flight data from a dump1090 endpoint
  response = requests.get(f'{DUMP1090_ENDPOINT}/data.json')
  data = response.json()

  # Get only the flight names from the data records
  flights = map(lambda record: record['flight'].strip(), data)

  # Return a set of flights which are not empty
  return set(filter(lambda name: name, flights))

# Helper function to iterate over a list and fn
def each(fn, items):
  for item in items:
    fn(item)

def get_history():
  try:
    with open("history.json", "r") as f:
      history = json.load(f)
  except FileNotFoundError:
    history = {}
  return history

def save_timestamp(flight):
  history = get_history()
  history[flight] = datetime.datetime.now().isoformat()
  with open("history.json", "w") as f:
    json.dump(history, f)

def should_send_alert(flight):
  history = get_history()
  # Check if we haven't logged this flight yet
  if flight not in history:
    return True
  # Calculate the total minutes since the last alert
  ts = datetime.datetime.fromisoformat(history[flight])
  delta = (datetime.datetime.now() - ts).total_seconds() / 60
  # Only send an alert if we last sent one 30 minutes ago or longer
  return delta >= 30

def send_alert(flights):
  # Save each flights 'last sent' timestamp
  each(lambda flight: save_timestamp(flight), flights)

  # Build up the body text / HTML
  flight_list = ', '.join(flights)
  BODY_TEXT = f"The following flights have been seen: {flight_list}"
  BODY_HTML = f"""<html><body><p>{BODY_TEXT}</p></body></html>"""

  try:
    # Attempt to send the email
    response = client.send_email(
      Destination={ 'ToAddresses': [ "you@example.com" ] },
      Message={
        'Body': {
          'Html': { 'Charset': CHARSET, 'Data': BODY_HTML },
          'Text': { 'Charset': CHARSET, 'Data': BODY_TEXT },
        },
        'Subject': { 'Charset': CHARSET, 'Data': f"Flight Alert - {flight_list}" },
      },
      Source="Flight Alert <you@example.com>"
    )
  # Display an error if something goes wrong.
  except ClientError as e:
    print(e.response['Error']['Message'])
  else:
    print(f"Alert sent ({flight_list}! Message ID:", response['MessageId']),

# Load the flights
flights = get_flights()

# Filter out any flights we are not interested in as well as
# any flights we should not send alert about (already sent recently)
targets = list(filter(lambda flight: flight in FLIGHTS_OF_INTEREST and should_send_alert(flight), flights))

# Send an alert for any flights of interest
if len(targets):
  send_alert(targets)

print('Total flights seen:', flights)