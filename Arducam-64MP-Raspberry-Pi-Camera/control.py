import atexit
import datetime
from Focuser import Focuser
import os
import readchar
from signal import SIGUSR1
import socket
from subprocess import Popen, DEVNULL
from time import sleep

# Configuration
FOCUS_STEP = 10
DEVICE = '/dev/v4l-subdev1'
FILE_FORMAT = '%Y_%m_%d_%H_%M_%S.png' # strftime.org
VIEWFINDER_WIDTH = 1920
VIEWFINDER_HEIGHT = 1080
# Max capture resolution is 9152x6944
CAPTURE_WIDTH = 3840
CAPTURE_HEIGHT = 2160
QUALITY = 100 # 0 - 100
DENOISE_MODE = 'cdn_hq' # auto, off, cdn_off, cdn_fast, cdn_hq

# Available commands
commands = {
  'capture': { 'key': readchar.key.SPACE },
  'focus-in': { 'key': 'q' },
  'focus-out': { 'key': 'e' },
  'auto-focus': { 'command': 'F', 'key': 'f' },
  'max-zoom': { 'command': 'M', 'key': ']' },
  'reset-zoom': { 'command': 'R', 'key': '[' },
  'zoom-in': { 'command': 'W', 'key': 'w' },
  'zoom-out': { 'command': 'S', 'key': 's' },
  'pan-frame-up': { 'command': 'I', 'key': readchar.key.UP },
  'pan-frame-down': { 'command': 'K', 'key': readchar.key.DOWN },
  'pan-frame-left': { 'command': 'J', 'key': readchar.key.LEFT },
  'pan-frame-right': { 'command': 'L', 'key': readchar.key.RIGHT },
  'exit': { 'command': 'X', 'key':'x' },
}

# Hotkey key names/values
key_names = list(filter(lambda key: '__' not in key, dir(readchar.key)))
key_values = list(map(lambda key_name: getattr(readchar.key, key_name), filter(lambda key: '__' not in key, dir(readchar.key))))

# Setup Focuser and socket for web control
focuser = Focuser(DEVICE)
s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=0)

# Zoom constants (should not be changed)
ZOOM_LEVEL = 0
ZOOM_MAX = 10

# Send a command to web-control
def send_command(cmd):
  s.sendto(cmd.encode('utf-8'), ('127.0.0.1', 8080))

# Shutdown the camera view process
def cleanup():
  p.kill()

# Handle renaming the captured image
def handle_post_capture():
  i = 0
  # Wait for image to be captured
  print('Waiting for capture to save...')
  while i < 30:
    i += 1
    # Once detected, break the loop
    if os.path.exists('.temp.png'):
      break
    # Otherwise, wait for one second and try again
    sleep(1)
  # If the request timed out, exit
  if i == 30:
    print('Image could not be saved')
    exit(1)
  # Rename the image from the temporary name to the date string
  name = datetime.datetime.now().strftime(FILE_FORMAT)
  os.rename(".temp.png", name)
  print('Saved capture to:', name)
  sleep(2)

# Print out a list of the hotkeys
def print_hotkeys():
    # Create a dict of the key values and names for reference
    keys = dict(zip(key_values, key_names))
    print('\n\t    Hotkeys:')
    print('\t', '-' * 14)
    for command, info in commands.items():
        # If the key does not exist in the dict, it's a normal letter-based key (ex. X)
        if info['key'] in keys.keys():
            key = keys[info['key']]
        else:
            key = info['key']
        print(f'{command.replace("-", " ").title().rjust(15)}: {key.title()}')
    print('\n')

# Print out the camera's focus and zoom status
def print_information():
    info = {
        'focus': focuser.get(Focuser.OPT_FOCUS),
        'zoom': ZOOM_LEVEL
    }
    print('\t  Information:\n\t', '-' * 14)
    for attr, value in info.items():
        print(f'{attr.title().rjust(15)}: {value}')

# Launch camera view
cmd = f'libcamera-still -t 0 --viewfinder-width {VIEWFINDER_WIDTH} --viewfinder-height {VIEWFINDER_HEIGHT} --quality {QUALITY} --denoise {DENOISE_MODE} --encoding png --signal --output .temp.png --width {CAPTURE_WIDTH} --height {CAPTURE_HEIGHT}'
p = Popen(cmd.split(' '), stdout=DEVNULL, stderr=DEVNULL)
# Add cleanup method for camera view
atexit.register(cleanup)

# Reset zoom to zero on launch
send_command(commands['reset-zoom']['command'])

# Remove any old temporary captures
if os.path.exists('.temp.png'):
  os.unlink('.temp.png')

while True:
  os.system('clear')

  # Display the module information (focus/zoom level)
  print_information()

  # Display the hotkeys
  print_hotkeys()

  # Wait for a key to be hit
  key = readchar.readkey()

  # Capture
  if key == commands['capture']['key']:
    # libcamera-still can trigger a capture if the '-s' flag is passed and SIGUSR1 is sent to the process
    p.send_signal(SIGUSR1)
    # Wait for the image to be created and rename to the date string
    handle_post_capture()

  # Focus
  elif key == commands['focus-in']['key']:
    focuser.set(Focuser.OPT_FOCUS, focuser.get(Focuser.OPT_FOCUS) - FOCUS_STEP)
  elif key == commands['focus-out']['key']:
    focuser.set(Focuser.OPT_FOCUS, focuser.get(Focuser.OPT_FOCUS) + FOCUS_STEP)

  # Zoom
  elif key == commands['zoom-in']['key']:
    if ZOOM_LEVEL == 10:
      continue
    ZOOM_LEVEL += 1
  elif key == commands['zoom-out']['key']:
    if ZOOM_LEVEL == 0:
      continue
    ZOOM_LEVEL -= 1

  # Determine if any of the commands were called
  cmd_name, cmd = next(filter(lambda x: key == x[1]['key'], commands.items()), (None, None))
  if cmd is not None:
    # Only send a command if needed
    if 'command' in cmd:
      send_command(cmd['command'])
    # Handle any post-command actions
    if cmd_name == 'reset-zoom':
      ZOOM_LEVEL = 0
    elif cmd_name == 'max-zoom':
      ZOOM_LEVEL = 10
    elif cmd_name == 'exit':
      exit(0)
