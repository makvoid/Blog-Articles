from colour import Color
from functools import reduce
from math import floor, modf

RGB_SCALER = lambda x: (round(x[0] * 255), round(x[1] * 255), round(x[2] * 255))

class Telemetry():
    '''Telemetry calculation'''
    _lap_stats = {'fuel': {}, 'dist': {}}

    def __init__(self, data = {}):
        self.data = data
        # Cache tire temperature colors in RGB 0-255 scale
        color_range = [c.rgb for c in Color('#00d0ff').range_to('#dd0000', 250)]
        self._tire_temperature_colors = list(map(RGB_SCALER, color_range))

    def seconds_to_lap_time(self, value):
        '''Convert seconds to lap time format (MM:SS:MS)'''
        minutes, seconds = map(floor, divmod(value, 60))
        # Convert decimal format ms to a readable format
        ms = floor(modf(value)[0] * 60)
        return '{:02}:{:02}:{:02}'.format(minutes, seconds, ms)

    def load(self, data):
        '''Load new data packet'''
        lap_num = self.get_value('lap_num')

        # Detect if we just started a new race
        if 'dist_traveled' in data and self.get_value('dist_traveled') == 0 and data['dist_traveled'] < 0:
            self.clear_stints()

        # Detect if we just started a new lap
        if 'lap_time_current' in self.data and self.get_value('lap_time_current') > data['lap_time_current']:
            # Ensure the game was not just paused
            if data['lap_time_current'] != 0:
                dist_start = reduce(lambda a, b: a + b, self._lap_stats['dist'].values(), 0)
                self._lap_stats['dist'][lap_num] = self.get_value('dist_traveled') - dist_start
                self._lap_stats['fuel'][lap_num] = self.get_value('fuel')

        self.data = data

    def clear_stints(self):
        '''Remove lap stint information such as fuel and distance'''
        self._lap_stats['fuel'].clear()
        self._lap_stats['dist'].clear()

    def get_value(self, key):
        '''Get a data packet value'''
        if key not in self.data.keys():
            return None
        return self.data[key]

    @property
    def lap_time(self):
        '''Convert the lap time to MM:SS:MS format'''
        return self.seconds_to_lap_time(self.get_value('lap_time_current'))

    @property
    def time_gain(self):
        '''Calculate the total lap time gain based on previous lap pace'''
        lap_num = self.get_value('lap_num')
        default_value = {'value': '+0.0', 'color': '#ffff00'}

        # Check if the first lap, ensure lap data is present
        if lap_num == 0:
            return default_value
        if lap_num - 1 not in self._lap_stats['dist'].keys():
            return default_value

        # Get the previous lap pace
        last_lap_dist = self._lap_stats['dist'][lap_num - 1]
        last_lap_dist_per_sec = last_lap_dist / self.get_value('lap_time_last')
        # Check if the dashboard was started after the race was started
        if last_lap_dist_per_sec == 0:
            return default_value
        last_lap_time_estimate_secs = last_lap_dist / last_lap_dist_per_sec

        # Get our current lap pace
        current_lap_dist = self.get_value('dist_traveled') - reduce(lambda a, b: a + b, self._lap_stats['dist'].values(), 0)
        current_lap_dist_per_sec = current_lap_dist / self.get_value('lap_time_current')
        current_lap_time_estimate_secs = last_lap_dist / current_lap_dist_per_sec

        # Return the delta between our current pace and last lap
        stint_delta = round(current_lap_time_estimate_secs - last_lap_time_estimate_secs, 1)
        return {
            'value': f'+{stint_delta}' if stint_delta > 0 else str(stint_delta),
            'color': '#dd0000' if stint_delta > 0 else '#51c651'
        }

    @property
    def fuel_percent_per_lap(self):
        '''Calculate the current fuel usage per lap'''
        # We are not in an active race
        if self.get_value('race_position') == 0:
            return '0.0%'

        # Check if this is the first lap (laps are 0-indexed)
        if self.get_value('lap_num') == 0:
            return f'{round((1 - self.get_value("fuel")) * 100, 1)}%'

        # Ensure the last lap's information is available
        last_lap_num = self.get_value('lap_num') - 1
        if last_lap_num not in self._lap_stats['fuel'].keys():
            return '0.0%'

        # Calculate the lap delta
        fuel_delta = self._lap_stats['fuel'][last_lap_num] - self.get_value('fuel')
        return f'{round(fuel_delta * 100, 1)}%'

    @property
    def fuel_level(self):
        '''Return the fuel level as a percentage'''
        return f'{round(self.get_value("fuel") * 100)}%'

    @property
    def gear(self):
        '''Return a letter representation of the gear'''
        gear_num = self.get_value('gear_num')
        if gear_num == 0:
            return 'R'
        elif gear_num == 11:
            return 'N'
        return str(gear_num)

    @property
    def speed(self):
        '''Return the vehicle speed (in MPH)'''
        return self.get_value('speed')

    @property
    def engine_load(self):
        '''Return the true engine load'''
        idle_rpm = self.get_value('engine_idle_rpm')
        max_rpm = self.get_value('engine_max_rpm')
        current_rpm = self.get_value('engine_current_rpm')
        # Ensure we are in a vehicle and not a menu
        if min(idle_rpm, max_rpm, current_rpm) == 0:
            return 0
        return (current_rpm - idle_rpm) / (max_rpm - idle_rpm)

    @property
    def tire_temperature(self):
        '''Calculate the tire temperature and a matching color'''
        temp = {
            'FL': {
                'value': self.get_value('tire_temp_FL')
            },
            'FR': {
                'value': self.get_value('tire_temp_FR')
            },
            'RL': {
                'value': self.get_value('tire_temp_RL')
            },
            'RR': {
                'value': self.get_value('tire_temp_RR')
            }
        }

        # Show green, red, or a blended color between the two depending on the temp
        for tire in temp.values():
            if tire['value'] < 100:
                tire['color'] = RGB_SCALER(Color('#00d0ff').rgb)
            elif tire['value'] >= 350:
                tire['color'] = RGB_SCALER(Color('#dd0000').rgb)
            else:
                value = floor(tire['value'] - 100)
                tire['color'] = self._tire_temperature_colors[value]

        return temp

    @property
    def wheel_slip(self):
        '''Calculate the wheel slip'''
        drivetrain_id = self.get_value('car_drivetrain_id')
        wheel_slip = {
            'FL': self.get_value('wheel_combined_slip_FL'),
            'FR': self.get_value('wheel_combined_slip_FR'),
            'RL': self.get_value('wheel_combined_slip_RL'),
            'RR': self.get_value('wheel_combined_slip_RR')
        }
        # FWD
        if drivetrain_id == 0:
            return {
                'left': wheel_slip['FL'] * 2,
                'right': wheel_slip['FR'] * 2
            }
        # RWD
        elif drivetrain_id == 1:
            return {
                'left': wheel_slip['RL'] * 2,
                'right': wheel_slip['RR'] * 2
            }
        # AWD
        return {
            # Average the value between both wheels
            'left': ((wheel_slip['FL'] + wheel_slip['RL']) / 2) * 2,
            'right': ((wheel_slip['FR'] + wheel_slip['RR']) / 2) * 2
        }
