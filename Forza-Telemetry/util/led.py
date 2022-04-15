from adafruit_aw9523 import AW9523
#from .adafruit_aw9523_mock import AW9523
from board import I2C
from json import load
from os import path
from time import sleep

# Instantiate the I2C interface
i2c = I2C()

class RGBColor():
    '''RGB Colors object'''
    off = (0, 0, 0)
    red = (10, 0, 0)
    green = (0, 10, 0)
    blue = (0, 0, 10)
    yellow = (10, 10, 0)
    orange = (20, 5, 0)

class LED():
    '''Individual LED controller class'''
    def __init__(self, driver, red_pin, green_pin, blue_pin):
        self.driver = driver
        self.pins = {
            'r': red_pin,
            'g': green_pin,
            'b': blue_pin
        }
        self._validate_pins()

    def set_color(self, red, green, blue):
        '''Set this LED to a specific RGB value'''
        self.driver.set_constant_current(self.pins['r'], min(255, red))
        self.driver.set_constant_current(self.pins['g'], min(255, green))
        self.driver.set_constant_current(self.pins['b'], min(255, blue))

    def _validate_pins(self):
        '''Validate the supplied pins passed and ensure they are valid'''
        for pin in [self.pins['r'], self.pins['g'], self.pins['b']]:
            if pin < 0 or pin > 15:
                address = self.driver.i2c_device.device_address
                raise Exception(f'Invalid pin number provided ({address}): {pin}')

class DashLEDController():
    '''Dashboard LED Controller'''
    _initialized = False
    _frames_at_limit = {}
    _led_state = {}

    def __init__(self, telemetry):
        self.telemetry = telemetry
        # Check if we have a controller configuration
        if not path.isfile('controller_config.json'):
            print('Error: controller_config.json is missing, unable to initialize devices.')
            return

        # Parse configuration json
        with open('controller_config.json', 'r') as f:
            self.controllers = load(f)

        # Instantiate library class for each controller
        for controller, config in self.controllers.items():
            self._frames_at_limit[controller] = 0
            self._led_state[controller] = {}
            config['driver'] = AW9523(i2c, int(config['device'], 16)) # Real
            #config['driver'] = AW9523(None, config['device'], None) # Mock
            config['driver'].LED_modes = 0xFFFF
            config['driver'].directions = 0xFFFF

            # Instantiate LED class for each LED
            config['leds'] = {}
            for led, pins in config['pins'].items():
                config['leds'][led] = LED(config['driver'], *pins)
                self._led_state[controller][led] = (0, 0, 0)

        # Set a flag so we know we can set LEDs without any errors
        self._initialized = True

        # Start a test sequence to ensure all LEDs are working
        self._test_leds()

    def set_led_value(self, controller, led_nums, red, green, blue):
        '''
            Set a specific controller's LEDs to an RGB value
            ex. set_led_value('tachometer', [1,3,5], *RGBColor.yellow)
        '''
        # Ensure LED controllers successfully initialized
        if not self._initialized:
            raise Exception('Error: LED Controllers not initialized')

        # Ensure the controller passed is of a valid name
        if controller not in self.controllers.keys():
            raise Exception(f'Invalid controller name provided: {controller}')

        # Convert singular LED pin to a list for loop
        if type(led_nums) in [str, int]:
            led_nums = [led_nums]
        elif type(led_nums) != list:
            raise Exception('Must pass a str, int or list for led_nums')

        # Loop through each provided pin number
        for led_num in led_nums:
            # Ensure the LED number provided is valid
            led_num = str(led_num)
            leds = self.controllers[controller]['leds']
            if led_num not in leds.keys():
                raise Exception(f'Error: Invalid LED number provided ({controller}): {led_num}')

            # Set the color via the utility function
            colors = (red, green, blue)
            if self._led_state[controller][led_num] != colors:
                leds[led_num].set_color(*colors)
                self._led_state[controller][led_num] = colors

    def clear_status(self):
        '''Turn off all controllers LEDs'''
        if not self._initialized:
            return
        for controller in self.controllers.keys():
            # Loop through each pin in each controller and turn it off
            for pin in range(1, 6):
                self.set_led_value(controller, pin, 0, 0, 0)

    def update_status(self):
        '''Update LED status based on current packet data'''
        if self._initialized:
            self._set_tachometer_led_status()
            self._set_wheel_slip_led_status()

    def _test_leds(self):
        if not self._initialized:
            return
        # Perform a test pattern
        for controller in self.controllers.keys():
            for direction in ['f', 'r']:
                pins = range(1,6) if direction == 'f' else range(5, 0, -1)
                for pin in pins:
                    self.set_led_value(controller, pin, *RGBColor.orange)
                    sleep(0.05)
                self.clear_status()

    def _set_wheel_slip_led_status(self):
        '''Set the wheel slip LED status (Private)'''
        wheel_slip = self.telemetry.wheel_slip
        for side in wheel_slip.keys():
            controller = f'wheel_{side}'
            # Reset our limit counter if it has decreased
            if wheel_slip[side] < 40:
                self._frames_at_limit[controller] = 0

            if wheel_slip[side] < 10:
                # Disable all other LEDs
                self.set_led_value(controller, list(range(1, 6)), *RGBColor.off)
            if wheel_slip[side] >= 10 and wheel_slip[side] < 20:
                self.set_led_value(controller, 1, *RGBColor.blue)
                self.set_led_value(controller, list(range(2, 6)), *RGBColor.off)
            elif wheel_slip[side] >= 20 and wheel_slip[side] < 30:
                self.set_led_value(controller, [1, 2], *RGBColor.blue)
                self.set_led_value(controller, list(range(3, 6)), *RGBColor.off)
            elif wheel_slip[side] >= 30 and wheel_slip[side] < 40:
                self.set_led_value(controller, list(range(1, 4)), *RGBColor.blue)
                self.set_led_value(controller, [4, 5], *RGBColor.off)
            elif wheel_slip[side] >= 20 and wheel_slip[side] < 30:
                self.set_led_value(controller, list(range(1, 5)), *RGBColor.blue)
                self.set_led_value(controller, 5, *RGBColor.off)
            elif wheel_slip[side] >= 30 and wheel_slip[side] < 40:
                self.set_led_value(controller, list(range(1, 6)), *RGBColor.blue)
            elif wheel_slip[side] >= 40:
                self._frames_at_limit[controller] += 1
                # Every 3 packets (0.03 sec) flash the LEDs
                # so it is more obvious we are at our limit
                if self._frames_at_limit[controller] % 3 == 0:
                    current = 15
                else:
                    current = 30
                self.set_led_value(controller, list(range(1, 6)), 0, 0, current)

    def _set_tachometer_led_status(self):
        '''Set the tachometer LED status (Private)'''
        load = self.telemetry.engine_load * 100
        # Reset our limit counter if it has decreased
        if load < 85:
            self._frames_at_limit['tachometer'] = 0

        if load < 40:
            # Disable all other LEDs
            self.set_led_value('tachometer', list(range(1, 6)), *RGBColor.off)
        if load >= 40 and load < 50:
            self.set_led_value('tachometer', 1, *RGBColor.green)
            self.set_led_value('tachometer', list(range(2, 6)), *RGBColor.off)
        elif load >= 50 and load < 60:
            self.set_led_value('tachometer', [1, 2], *RGBColor.green)
            self.set_led_value('tachometer', list(range(3, 6)), *RGBColor.off)
        elif load >= 60 and load < 70:
            self.set_led_value('tachometer', list(range(1, 4)), *RGBColor.green)
            self.set_led_value('tachometer', list(range(4, 6)), *RGBColor.off)
        elif load >= 70 and load < 80:
            self.set_led_value('tachometer', list(range(1, 4)), *RGBColor.green)
            self.set_led_value('tachometer', 4, *RGBColor.blue)
            self.set_led_value('tachometer', 5, *RGBColor.off)
        elif load >= 80 and load < 85:
            self.set_led_value('tachometer', list(range(1, 4)), *RGBColor.green)
            self.set_led_value('tachometer', [4, 5], *RGBColor.blue)
        elif load >= 85:
            self._frames_at_limit['tachometer'] += 1
            # Every 3 packets (~0.03 sec) flash the LEDs
            # so it is more obvious we are at our rev limit
            if self._frames_at_limit['tachometer'] % 3 == 0:
                current = 15
            else:
                current = 30
            self.set_led_value('tachometer', list(range(1, 6)), current, 0, 0)
