# Interactive LED Strip
Underlying code behind how I built an internet-controllable LED strip using Adafruit's DotStar strip, a D1 Mini (ESP8266) and Angular.

**Medium Article Link**: [Link](https://betterprogramming.pub/building-an-internet-controllable-led-strip-cdbe1c846cd5)

---

## Components

### Frontend
Angular UI to allow Users to select new colors to send to the microcontroller.

### Microcontroller
MicroPython code and libraries required to run the DotStar/WebSocket code. I used a D1 Mini so the pins are configured as so but this code is compatible with any microcontroller.

### Server
Node JS script to serve a simple WebSocket server to allow Users to send new color requests and then relay that new choice to the microcontroller.