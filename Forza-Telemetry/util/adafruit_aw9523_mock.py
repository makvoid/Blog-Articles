class I2CDeviceMock():
    '''Mock I2CDevice class with no functions simulated'''
    def __init__(self, _, address):
        self.device_address = address

class AW9523():
    '''Mock AW9523 class with the basic LED functions simulated/logged'''
    _LED_MODES = None
    _directions = None
    pins = {}

    def __init__(self, i2c_bus, address, _):
        self.i2c_bus = i2c_bus
        self.i2c_device = I2CDeviceMock(None, address)
        for i in range(0, 16):
            self.pins[i] = 0
        self._log('Registered device')

    def _log(self, *msg):
        address = self.i2c_device.device_address
        print(f'[AW9523-Mock-{address}]', *msg)

    def set_constant_current(self, pin, value):
        if pin < 0 or pin > 15:
            raise ValueError('Pin must be 0 to 15')
        if value < 0 or value > 255:
            raise ValueError('Value must be 0 to 255')
        self.pins[pin] = value
        self._log('Set pin', pin, 'to', value)

    def get_pin(self, pin):
        return self.pins[pin]

    @property
    def directions(self):
        return ~self._directions & 0xFFFF

    @directions.setter
    def directions(self, dirs):
        self._directions = (~dirs) & 0xFFFF
        self._log('Set directions to', (~dirs) & 0xFFFF)

    @property
    def LED_modes(self):
        return ~self._LED_modes & 0xFFFF

    @LED_modes.setter
    def LED_modes(self, modes):
        self._LED_modes = ~modes & 0xFFFF
        self._log('Set LED_modes to', ~modes & 0xFFFF)
