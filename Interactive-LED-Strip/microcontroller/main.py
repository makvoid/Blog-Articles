from config import config
from machine import SPI, Pin
from micropython_dotstar import DotStar
from network import WLAN, STA_IF
from time import sleep, time
import uwebsockets.client

# Setup the network
network = WLAN(STA_IF)
network.active(True)
network.connect(config['wifi_name'], config['wifi_password'])
start = time()
# Wait until the network is connected
while not network.isconnected():
  # Ensure we have not waited longer than our timeout
  if time() - start > config['wifi_connect_timeout']:
    print('Unable to connect to the network within time limit, exiting...')
    exit(1)
  print('Still waiting for a network connection...')
  sleep(1)
print('Network address:', network.ifconfig()[0])

# Limit a value between two values
def clamp(num, min_val, max_val):
  return max(min(num, max_val), min_val)

# Helper function to create the websocket connection/timeout
def create_websocket():
  print('Creating websocket connection...')
  try:
    ws = uwebsockets.client.connect(config['ws_url'])
    ws.settimeout(5)
  except:
    print(f'Error creating websocket, trying again shortly...')
    sleep(config['ws_connection_delay'])
    return create_websocket()
  return ws

# Setup websocket connection
websocket = create_websocket()

# Setup SPI/DotStar
spi = SPI(
  sck=Pin(config['sck_pin']),
  mosi=Pin(config['mosi_pin']),
  miso=Pin(config['miso_pin'])
)
dotstar = DotStar(spi, config['num_dotstars'])

# Wait for a websocket message
while True:
  # Attempt to receive a message
  msg = None
  try:
    msg = websocket.recv().replace('"', '').split(',')
  except Exception as e:
    print('Error during receive:', e)

  # If we received a message, format the values and update the DotStar array
  if msg:
    # If we receive a blank message, this is most likely the websocket dropping
    if len(msg) == 1:
      websocket = create_websocket()
      continue

    # Format the tuple and set the color
    color = (
      clamp(int(msg[0]), 0, 255), # Red
      clamp(int(msg[1]), 0, 255), # Green
      clamp(int(msg[2]), 0, 255), # Blue
      clamp(float(msg[3]), 0, 1)  # Brightness
    )
    dotstar.fill(color)
    print('Color set to', color)

  # Send a blank message (to help w/ closed sockets)
  try:
    websocket.send('')
  except:
    websocket = create_websocket()
    continue

print('Done!')
