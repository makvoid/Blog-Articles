import machine

class Vector3D:
    def __init__(self, x = 0, y = 0, z = 0):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f'{{X: {self.x}, Y: {self.y}, Z: {self.z}}}'

    def as_tuple(self):
        return (self.x, self.y, self.z)

class AccelerometerData:
    def __init__(self, raw):
        self.accel = Vector3D(
                self.bytes_to_int(raw[0], raw[1]),
                self.bytes_to_int(raw[4], raw[5]),
                self.bytes_to_int(raw[2], raw[3]),
        )
        self.gyro = Vector3D(
                self.bytes_to_int(raw[8], raw[9]),
                self.bytes_to_int(raw[12], raw[13]),
                self.bytes_to_int(raw[10], raw[11]),
        )
        # Convert temperature to Celsius
        self.temp = self.bytes_to_int(raw[6], raw[7]) / 340.00 + 36.53

    def __repr__(self):
        return f'{{Accel: {self.accel}, Gyro: {self.gyro}, Temp: {self.temp}}}'

    def bytes_to_int(self, a, b):
        if not a & 0x80:
            return a << 8 | b
        return - (((a ^ 255) << 8) | (b ^ 255) + 1)

class Accelerometer():
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.start()
        self.i2c.writeto(self.addr, bytearray([107, 0]))
        self.i2c.stop()

    def get_raw_values(self):
        self.i2c.start()
        data = self.i2c.readfrom_mem(self.addr, 0x3B, 14)
        self.i2c.stop()
        return data

    def get_values(self):
        return AccelerometerData(self.get_raw_values())
