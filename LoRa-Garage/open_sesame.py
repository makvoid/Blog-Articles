from adafruit_rfm9x import RFM9x
import board
from busio import SPI, UART
from digitalio import DigitalInOut, Direction
from gc import collect
from math import sin, cos, sqrt, atan2, radians
from struct import pack, unpack
from supervisor import ticks_ms
from time import monotonic, sleep

from config import config

if config['mode'] == 'car':
  from adafruit_gps import GPS

# next's default value is not available in Circuit Python
# (this is a painless workaround)
def first_true(iterable, default, predicate):
  try:
    return next(filter(predicate, iterable))
  except StopIteration:
    return default

# Message packet helper
class MessagePacket():
  _msg_format = '4H'

  def __init__(self):
    self.id = int(str(ticks_ms())[-4:])
    self.created_at = monotonic()

  def __eq__(self, other):
    return int(self.id) == int(other.id)

  # Update this object to the desired message
  def update(self, channel, message, target = 0, msg_id = 0):
    self.channel = int(channel)
    self.message = int(message)
    self.target = int(target)
    if msg_id != 0:
      self.id = int(msg_id)

  # Parse an incoming message
  def parse(self, raw_msg):
    try:
      msg_id, channel, message, target = unpack(self._msg_format, raw_msg)
    except Exception as e:
      print('Unable to parse message', raw_msg, e)
      return
    self.id = int(msg_id)
    self.channel = int(channel)
    self.message = int(message)
    self.target = int(target)

  def dump(self):
    return pack(self._msg_format, self.id, self.channel, self.message, self.target)

class OpenSesame():
  # Active messages
  messages = []

  # Used for door state
  state = {
    'activated': False,
    'opened': False
  }

  def __init__(self, debug = False):
    self.debug = debug
    # Setup mode-specific requirements
    if config['mode'] == 'car':
      # Setup UART / GPS
      self.uart = UART(board.TX, board.RX, baudrate=9600, timeout=10)
      self.gps = GPS(self.uart, debug=self.debug)
      self.gps.send_command(bytes(config['gps']['modes'][config['gps']['mode']], "utf-8"))
      self.gps.send_command(bytes(f"PMTK220,{config['gps']['update_rate_ms']}", "utf-8"))
    elif config['mode'] == 'garage':
      # Setup Relay
      self.relay = DigitalInOut(config['relay']['pin'])
      self.relay.direction = Direction.OUTPUT
    else:
      raise Exception(f"Unknown mode: {config['mode']}")

    # Setup LED
    self.led = DigitalInOut(board.D13)
    self.led.direction = Direction.OUTPUT

    # Setup LoRa module
    self.spi = SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    self.rfm9x = RFM9x(self.spi, DigitalInOut(board.RFM9X_CS), DigitalInOut(board.RFM9X_RST), config['lora']['freq_mhz'])
    self.rfm9x.tx_power = config['lora']['tx_power_db']

  def run(self):
    last_print = monotonic()
    while True:
      # Attempt to receive a packet
      self._parse_incoming_packet()

      # Check for a GPS update
      if config['mode'] == 'car':
        collect()
        self.gps.update()

      # Run every second
      current = monotonic()
      if current - last_print >= 1.0:
        last_print = current

        # Check for any messages we should resend
        self._check_messages()

        # If this is the car, do some distance checks
        if config['mode'] == 'car':
          self._check_position()

  # Packet parsing
  def _parse_incoming_packet(self):
    # Attempt to receive a packet
    packet = self.rfm9x.receive(timeout=config['lora']['msg_timeout_secs'])

    # Did we receive a packet?
    if packet is not None:
      packet = MessagePacket()
      # Attempt to parse the message
      packet_text = str(packet, "ascii")
      try:
        packet.parse(packet_text)
      except Exception as e:
        print(f'Unable to parse message: {packet_text}, {e}')
        return

      # Ensure this message is for our channel
      if packet.channel != config['channel']:
        return

      # Check if this is a reply to one of our messages
      self._check_message(packet)

      # Execute underlying command logic
      return self._execute_packet_command(packet)

  def _execute_packet_command(self, packet):
    if packet.message == config['messages']['ping']:
      # Send pong reply
      self._send_message(config['messages']['pong'], packet.id)
    elif packet.message == config['messages']['pong']:
      # Log pong reply
      self._send_message(config['messages']['ack'], packet.id)
    elif packet.message == config['messages']['trigger'] and config['mode'] == 'garage':
      # Toggle the relay on/off to open the garage door
      self.relay.value = True
      sleep(config['relay']['delay_secs'])
      self.relay.value = False
      self._send_message(config['messages']['ack'], packet.id)
    elif packet.message != config['messages']['ack']:
      print(f'Unknown command message: {packet.message}')
      return
    self._blink_led()

  def _check_message(self, packet):
    message = first_true(self.messages, None, lambda msg: msg.id == packet.target)
    if message is not None:
      # If the message was found, remove it from the list
      self.messages = list(filter(lambda msg: msg.id != packet.target, self.messages))

  def _check_messages(self):
    now = monotonic()
    for message in self.messages:
      # Check if this message has gone over our timeout limit without a reply
      if now - message.created_at >= config['ack_timeout_secs']:
        # Resend the message and reset the created time
        message.created_at = monotonic()
        self._send_message(message.message, message.target, True, message.id)

  def _send_message(self, message, target = 0, is_resend = False, msg_id = 0):
    # Create a new packet
    packet = MessagePacket()
    packet.update(config['channel'], message, target, msg_id)

    # We don't need to track acknowledgement messages or re-sends
    if not is_resend and message != config['messages']['ack']:
      self.messages.append(packet)

    # Send the message
    self.rfm9x.send(packet.dump())

  def _check_position(self):
    # Ensure we have a GPS fix (location determined)
    if not self.gps.has_fix:
      print("Waiting for fix...")
      return

    # Check if we need to activate the trigger zone check
    if not self.state['activated'] and self._get_distance_to_trigger() >= config['gps']['trigger_zone']['activation_radius_meters']:
      self.state['activated'] = True
      print('Trigger zone activated')

    # If the trigger zone is activated and the door is closed, check if we are close enough to open it
    if self.state['activated'] and not self.state['opened'] and self._get_distance_to_trigger() <= config['gps']['trigger_zone']['radius_meters']:
      self._send_message(config['messages']['trigger'])
      self.state['opened'] = True
      print('Sent door open message!')

  def _blink_led(self):
    self.led.value = True
    sleep(0.05)
    self.led.value = False

  def _get_distance_to_trigger(self):
    trigger_zone = config['gps']['trigger_zone']
    lat1, lon1 = [radians(trigger_zone['lat']), radians(trigger_zone['lon'])]
    lat2, lon2 = [radians(self.gps.latitude), radians(self.gps.longitude)]

    # Use the Haversine formula to calculate the distance
    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Multiply our result by the radius of the Earth (in meters)
    return c * (6371 * 1000)
