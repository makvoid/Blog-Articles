# Article / Documentation
* **Medium Article Link**: [Link](https://medium.com/@makvoid/building-a-digital-dashboard-for-forza-using-python-62a0358cb43b)

# Requirements
* Python 3.6+
* Raspberry Pi 3B+ or Raspberry Pi 4 (Zero 2 was too slow even with an Ethernet hat)

# Installation / How to run
```sh
cp config.json.example config.json # Edit as needed
cp controller_config.json.example controller_config.json # Edit as needed
apt install -y libgtk-3-dev build-essential
python3 -m pip install -r requirements.txt
# Optionally, use PiWheels.org to skip building packages
DISPLAY=":0" python3 dashboard.py
```

# Key Shortcuts
* *F10* - Clear lap information (fuel/lap time gain)
* *F11* - Full-screen toggle for dashboard
* *ESC* - Exit the dashboard gracefully
