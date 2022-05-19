import adafruit_ahtx0
from adafruit_datetime import datetime
from adafruit_requests import Session
import board
from busio import I2C
from digitalio import DigitalInOut, Direction
from socketpool import SocketPool
from ssl import create_default_context
from time import monotonic, sleep
from wifi import radio

try:
    from secrets import secrets
except ImportError:
    print('Be sure to setup secrets.py for wifi secrets!')
    raise

# Setup an LED
def setup_led(led_pin):
    led = DigitalInOut(getattr(board, led_pin))
    led.direction = Direction.OUTPUT
    # Ensure the LED is off
    led.value = False
    return led

# Blink an LED
def blink_led(led_pin = 'LED_WHITE'):
    led = leds[led_pin]
    led.value = not led.value
    sleep(0.1)
    led.value = not led.value

# Setup I2C and AHT20 sensor
i2c = I2C(board.IO7, board.IO8)
sensor = adafruit_ahtx0.AHTx0(i2c)

# Setup the LEDs available on this board
led_pins = ['LED_RED', 'LED_GREEN', 'LED_BLUE', 'LED_WHITE', 'LED_YELLOW']
leds = dict(zip(led_pins, map(lambda led_pin: setup_led(led_pin), led_pins)))

# Connect to the WiFi network
radio.connect(secrets['wireless_name'], secrets['wireless_password'])
# Create socket pool
pool = SocketPool(radio)
# Create requests Session object
requests = Session(pool, create_default_context())

last = monotonic()
while True:
    # Only check once per second
    if monotonic() - last < 1:
        continue
    last = monotonic()
    now = datetime.now()
    # Every 15 minutes, sample the sensor
    if now.minute % 15 == 0 and now.second == 0:
        data = { 'temperature': sensor.temperature, 'humidity': sensor.relative_humidity }
        res = requests.post('https://jsonplaceholder.typicode.com/posts', data=data)
        print('Response from API:', res.json())
    # Every 30 seconds blink the LED
    if now.second % 30 == 0:
        blink_led()
