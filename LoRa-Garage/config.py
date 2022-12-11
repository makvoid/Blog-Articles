from board import A0

config = {
  # Device Mode
  'mode': 'car', # 'car', 'garage'
  'channel': 1,

  # How long to wait for an acknowledgement before resending the message
  'ack_timeout_secs': 5,

  # Messages
  'messages': {
    'ack': 0,
    'ping': 1,
    'pong': 2,
    'trigger': 3
  },

  # Relay settings
  'relay': {
    # Which pin on the Feather the relay is connected to
    'pin': A0,
    # How long to activate the relay
    'delay_secs': 0.1
  },

  # LoRa settings
  'lora': {
    # Frequency (433, 868, 915)
    'freq_mhz': 915.0,
    # How long to wait for a message
    'msg_timeout_secs': 1,
    # How much gain to use (23 db max for Adafruit's RFM9x)
    'tx_power_db': 23
  },

  # GPS settings
  'gps': {
    # How often to fetch an update
    'update_rate_ms': 1000,
    # Garage door opening zone
    'trigger_zone': {
      'lat': 29.888130,
      'lon': -90.193034,
      # How far from the trigger zone we should trigger
      'radius_meters': 15,
      # How far we have to drive away from the trigger point to activate it
      # (otherwise, it will trigger as we leave the neighborhood and not as we come back as intended)
      'activation_radius_meters': 250
    },
    # Which mode to use
    'mode': 'rmc_loc',
    'modes': {
      # Basic GGA and RMC info
      'gga_rmc': 'PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0',
      # RMC only and location
      'rmc_loc': 'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0',
      # All disabled
      'off': 'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0',
      # All enabled (not fully supported by the library)
      'all': 'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0'
    }
  }
}
