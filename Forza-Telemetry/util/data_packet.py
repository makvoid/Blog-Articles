from struct import unpack

class DataPacket():
    '''
        DataPacket - Validate and parse Forza Telemetry Data Packets from
        any recent Forza game (Forza Motorsport 7, Forza Horizon 4+).
    '''
    # Default sled format
    _default_format = '<iI27f4i20f5i'

    # Dash format (FM7)
    _dash_format = _default_format + '17fH6B3b'

    # Horizon format (FH4+)
    _horizon_format = _default_format + 'i19fH6B4b'

    # Expected packet lengths for each format
    _packet_lengths = {
        'sled': 232,
        'dash': 311,
        'fh4+': 324,
    }

    def __init__(self, version = 'sled'):
        '''
            Forza Data Packet Parser
            (version = sled, dash, fh4+)
        '''
        # Setup packet format and attributes
        self.packet_version = version
        if self.packet_version == 'sled':
            self._packet_format = self._default_format
        elif self.packet_version == 'dash':
            self._packet_format = self._dash_format
        elif self.packet_version == 'fh4+':
            self._packet_format = self._horizon_format
        else:
            raise ValueError(f'Unsupported packet version: {self.packet_version}, expected sled, dash, or fh4')

        # Assign attributes based on the packet version
        self.attributes = self.get_attributes()

    def __str__(self):
        '''Handle string representation of the class'''
        # Build a list of each attribute in string format
        attributes = map(lambda attr: f'{attr}={getattr(self, attr)}', self.attributes)
        return f"{type(self).__name__}({', '.join(attributes)})"

    def parse(self, packet, recording = False):
        '''Parse an incoming data packet'''
        size = len(packet)
        expected_size = self._packet_lengths[self.packet_version]
        # Ensure packet is the correct size
        if expected_size != size:
            # Attempt to find a match for this packet size
            try:
                match = next(filter(lambda x: x[1] == size, self._packet_lengths.items()))
                extra = f'- this looks like a {match[0]} data packet.'
            except:
                extra = ''
            raise ValueError(f'Invalid {self.packet_version} packet length {size}, expected {expected_size} {extra}')

        # Setup each value as an attribute on the class
        for name, value in zip(self.attributes, unpack(self._packet_format, packet)):
            # If we are recording data packets, do not convert any
            # values as these will be converted later in the process
            value = value if recording else self._convert(name, value)
            setattr(self, name, value)

    def get_attributes(self):
        '''
            Return the list of attributes applicable
            to the configured packet version
        '''
        if self.packet_version == 'sled':
            return self._get_default_attributes()
        elif self.packet_version == 'dash':
            return self._get_default_attributes() + \
                self._get_dash_attributes()
        elif self.packet_version == 'fh4+':
            return self._get_default_attributes() + \
                ['car_type', 'impact_x', 'impact_y'] + \
                self._get_dash_attributes() + \
                ['unknown'] # 1 byte undocumented attribute

    def to_dict(self):
        '''Convert the attributes to a dictionary'''
        return dict(zip(self.attributes, map(lambda attr: getattr(self, attr), self.attributes)))

    def _convert(self, key, value):
        '''Convert incoming value if applicable'''
        if key == 'speed':
            return round(value * 2.237) # m/s to mph
        elif key == 'power':
            return round(max(0, value / 746), 4) # Watt to hp
        elif key == 'torque':
            return round(max(0, value / 1.356), 4) # Newton meter to ft lbs
        elif key in ['throttle', 'brake', 'clutch', 'handbrake']:
            return round(value / 255 * 100) # Convert to percentage
        elif key == 'suspension_travel':
            return round(value * 39.37, 4) # Convert meter to inches
        # Round any other floats to at most 4 decimal places
        if type(value) == float:
            return round(value, 4)
        return value

    def _get_default_attributes(self):
        '''Returns the default/sled attributes'''
        return [
            'active', 'timestamp',
            'engine_max_rpm', 'engine_idle_rpm', 'engine_current_rpm',
            # X = right, Y = up, Z = forward
            *self._attr_axes_generator('acceleration'),
            # X = right, Y = up, Z = forward
            *self._attr_axes_generator('velocity'),
            # X = pitch, Y = yaw, Z = roll
            *self._attr_axes_generator('angular_velocity'),
            'yaw', 'pitch', 'roll',
            # 0.0 = max stretch, 1.0 = max compression
            *self._attr_wheel_generator('suspension_travel_ratio'),
            # 0 = 100% grip, any less means a loss of grip
            *self._attr_wheel_generator('wheel_slip_ratio'),
            # Wheel rotation speed (in radians per second)
            *self._attr_wheel_generator('wheel_rotation_speed'),
            # 1 = wheel on rumble strip, 0 = off
            *self._attr_wheel_generator('wheel_on_rumble_strip'),
            # 1.0 = deepest puddle, 0.0 = no puddle
            *self._attr_wheel_generator('wheel_puddle_depth'),
            # Surface rumble for controller force feedback
            *self._attr_wheel_generator('surface_rumble'),
            # 0 = 100% grip, any less means a loss of grip
            *self._attr_wheel_generator('wheel_slip_angle'),
            # 0 = 100% grip, any less means a loss of grip
            *self._attr_wheel_generator('wheel_combined_slip'),
            # Amount of suspension travel (converted to inches)
            *self._attr_wheel_generator('suspension_travel'),
            'car_ordinal_id', 'car_class_id', 'car_performance_index',
            # 0 = FWD, 1 = RWD, 2 = AWD
            'car_drivetrain_id', 'car_num_cylinders'
        ]

    def _get_dash_attributes(self):
        '''Returns the dash attributes (FM7, FH4+)'''
        return [
            # World position
            *self._attr_axes_generator('position'),
            'speed', 'power', 'torque',
            # Tire temperature in F
            *self._attr_wheel_generator('tire_temp'),
            'boost', 'fuel', 'dist_traveled',
            # Lap times (in seconds)
            'lap_time_best', 'lap_time_last', 'lap_time_current',
            'race_time', 'lap_num', 'race_position',
            # Amount of applied force
            'throttle', 'brake', 'clutch', 'handbrake',
            'gear_num', 'steering_angle',
            # In-race values
            'driving_line', 'ai_brake_diff'
        ]

    def _attr_axes_generator(self, key):
        '''Formats attribute key axes'''
        return [
            f'{key}_x', f'{key}_y', f'{key}_z'
        ]

    def _attr_wheel_generator(self, key):
        '''Formats attribute key wheels'''
        return [
            f'{key}_FL', f'{key}_FR',
            f'{key}_RL', f'{key}_RR'
        ]