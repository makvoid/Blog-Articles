config = {
    # API URL
    'api_url': 'https://1.2.3.4/api',

    # Unique ID
    'sensor_id': 'machine-trigger-dryer',

    # Wireless details
    'wifi_name': 'your_wifi_name_here',
    'wifi_password': 'your_wifi_pw_here',
    'wifi_connect_timeout': 30,

    # Pin connections
    'led_pin': 2,
    'sda_pin': 4,
    'scl_pin': 5,
    'btn_start_pin': 14,
    'btn_reset_pin': 12,
s
    # How many points over the baseline should be considered still running
    'value_threshold': 15,

    # Number of averages (minutes) above the baseline that will trigger the
    # 'machine finished' logic.
    # For example, 2 would trigger a 'done' alert when 3 minutes or more of averages
    # are no longer considered 'running'.
    'trigger_threshold': 2,

    # Control values for when the machine is not running
    'control_values': [2499.82, 2498.1, 2498.19, 2497.18, 2501.73]
}
