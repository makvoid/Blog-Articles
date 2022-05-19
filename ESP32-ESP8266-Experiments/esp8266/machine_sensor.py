from config import config
from machine import I2C, Pin, RTC, freq
from math import sqrt
import mpu_6050
from network import WLAN, STA_IF
from sys import exit
from time import sleep, ticks_ms, time
from urequests import post

class SensorMode():
    idle = 1
    running = 2

class MachineSensor():
    mode = SensorMode.idle
    _btn_state = { 'start': 0, 'reset': 0 }
    sensor_averages = []
    sensor_latest = []

    def __init__(self, dry_run = False):
        self.dry_run = dry_run

        # Setup I2C and the MPU6050 accelerometer
        self._i2c = I2C(scl=Pin(config['scl_pin']), sda=Pin(config['sda_pin']))
        self.imu = mpu_6050.Accelerometer(self._i2c)

        # Setup the buttons
        self._start_btn = Pin(config['btn_start_pin'], Pin.IN, Pin.PULL_UP)
        self._reset_btn = Pin(config['btn_reset_pin'], Pin.IN, Pin.PULL_UP)

        # Setup the LED
        self._led_pin = Pin(config['led_pin'], Pin.OUT)
        self._led_pin.value(1) # Ensure the LED is off

        # Connect to wifi
        self._connect_to_wifi()

        print('Awaiting command...')

    def run(self):
        last = ticks_ms()
        while True:
            # Handle tick logic
            time_now = ticks_ms()
            if time_now - last < 100:
                continue
            last = time_now
            now = self._get_datetime()

            # Detect if either button was pressed
            if self._start_btn.value() and self._reset_btn.value():
                exit(0)
            if self._start_btn.value() and not self._btn_state['start']:
                print('Start button pressed!')
                self._change_mode(SensorMode.running)
                # If it is already running, drain the data to restart
                if self.mode == SensorMode.running:
                    self._drain_data()
                self._blink_led(2)
            if self._reset_btn.value() and not self._btn_state['reset']:
                print('Reset button pressed!')
                # Switch mode to idle, drain the data
                self._change_mode(SensorMode.idle)
                self._drain_data()
                self._blink_led(5)

            # Update button state
            self._btn_state = { 'start': self._start_btn.value(), 'reset': self._reset_btn.value() }

            # Collect sample every 5 seconds
            if self.mode == SensorMode.running and now['subseconds'] < 100:
                # Collect a sample every 5 seconds
                if now['seconds'] % 5 == 0:
                    self._blink_led()
                    data = self.imu.get_values()
                    movement = self._calc_movement(data.accel.as_tuple())
                    print('Data:', data, 'Movement Total:', movement)
                    self.sensor_latest.append(movement)
                # At the top of the minute, calculate the average
                if now['seconds'] == 0:
                    # Enable the high frequency for quicker execution
                    self._set_frequency('high')
                    # Add the latest average
                    if len(self.sensor_latest):
                        self.sensor_averages.append(self._calc_average(self.sensor_latest))
                        self.sensor_latest.clear()
                    # Truncate the oldest average
                    if len(self.sensor_averages) > 5:
                        self.sensor_averages = self.sensor_averages[1:]
                    # Check if the machine is still running
                    if len(self.sensor_averages) == 5:
                        if self.dry_run:
                            print('Averages:', self.sensor_averages)
                        # Calculate the deltas between the control values and the latest averages
                        deltas = list(map(lambda x: max(x) - min(x), zip(config['control_values'], self.sensor_averages)))
                        # Count how many of those deltas are over our value threshold
                        triggers = len(list(filter(lambda x: x >= config['value_threshold'], deltas)))
                        print(triggers, 'averages over the control!')
                        # Check if the machine is still running
                        if triggers <= config['trigger_threshold']:
                            print('The machine looks like it has finished!')
                            try:
                                update = self._trigger_alert().json()
                                print('Response:', update['message'])
                            except:
                                pass
                            self._change_mode(SensorMode.idle)
                        else:
                            print('The machine is still running!')
                    # Switch back to the regular frequency
                    self._set_frequency('low')

    def _calc_movement(self, sample):
        x, y, z = map(lambda x: x / 10, sample)
        return sqrt(x*x + y*y + z*z)

    def _calc_average(self, samples):
        return sum(samples) / len(samples)

    def _change_mode(self, new_mode):
        # Grab human readable mode names
        modes = list(filter(
            lambda x: x[:2] != '__', SensorMode.__dict__.keys()
        ))
        # Match up the new requested mode with it's human readable name
        mode_name = next(filter(lambda x: getattr(SensorMode, x) == new_mode, modes))
        print('Mode changed to', mode_name)
        self.mode = new_mode

    def _connect_to_wifi(self):
        self.network = WLAN(STA_IF)
        self.network.active(True)
        self.network.connect(config['wifi_name'], config['wifi_password'])
        start = time()
        # Wait until the network is connected
        while not self.network.isconnected():
            # Ensure we have not waited longer than our timeout
            if time() - start > config['wifi_connect_timeout']:
                print('Unable to connect to the network within time limit, exiting...')
                exit(0)
            print('Still waiting for a network connection...')
            sleep(1)
        print('Network address:', self.network.ifconfig()[0])

    def _set_frequency(self, level):
        if level == 'high':
            hertz = 160
        elif level == 'low':
            hertz = 80
        else:
            raise Exception(f'Unknown frequency level: {level}')
        # Convert to megahertz
        freq(int(hertz * 1e+6))

    def _trigger_alert(self):
        if self.dry_run:
            return { 'message': 'Debug return for dry-run' }
        return post(
            config['api_url'],
            json={'type': config['sensor_id']}
        )

    def _blink_led(self, times = 1):
        for _ in range(times):
            self._led_pin.value(0)
            sleep(0.05)
            self._led_pin.value(1)
            # If more than one blink, insert a delay between blinks
            if times > 1:
                sleep(0.25)

    def _get_datetime(self):
        year, month, day, weekday, hours, minutes, seconds, subseconds = RTC().datetime()
        return {
            'year': year,
            'month': month,
            'day': day,
            'weekday': weekday,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'subseconds': subseconds
        }

    def _drain_data(self):
        self.sensor_averages.clear()
        self.sensor_latest.clear()
