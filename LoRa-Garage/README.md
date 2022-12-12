# LoRa CircuitPython Garage System

Underlying code behind a LoRa communication system I built to remotely open a garage door. Uses Adafruit's Ultimate GPS to obtain the device's location and calculates the distance to a fixed point. LoRa communication is used to send an event to a node using an Adafruit Power Relay which is hooked up to the garage door's button to open it.

* Medium Article Link: [Link](https://medium.com/gitconnected/using-radio-frequency-and-python-to-control-the-world-52d99aa9cece)

As the Feather devices are quite limited on memory, it is advisable to compile all of the code using [mpy-cross](https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library?view=all#mpy-3106477).

## Requirements
* `adafruit_gps` library