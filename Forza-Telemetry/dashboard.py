from json import load
from multiprocessing import Manager, Process
from os import path
import wx

from util.led import DashLEDController
from util.telemetry import Telemetry
from util.ui import UIElements
from workers.dashboard_background import worker

class DashboardFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # Instantiate utility classes
        self.ui = UIElements()
        self.telemetry = Telemetry()
        self.led_controller = DashLEDController(self.telemetry)

        # Setup initial style and frame properties
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        self.SetCursor(wx.Cursor(wx.CURSOR_BLANK))

        # Set window properties & start timer
        self._set_window_properties()
        self._start_timer()

        # Create the main window panel
        self.main_panel = wx.Panel(self, wx.ID_ANY)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a horizontal sizer to hold the columns
        column_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(column_sizer, 1, wx.EXPAND, 0)

        # Create the left-side column
        self.column_a = wx.BoxSizer(wx.VERTICAL)
        column_sizer.Add(self.column_a, 1, wx.EXPAND, 0)

        # Draw UI elements
        self.ui.draw_tire_temperature_elements(self)
        self.ui.draw_fuel_elements(self)

        # Create the middle column
        self.column_b = wx.BoxSizer(wx.VERTICAL)
        column_sizer.Add(self.column_b, 1, wx.EXPAND, 0)

        # Draw UI Elements
        self.ui.draw_gear_and_speed_elements(self)

        # Create the right-side column
        self.column_c = wx.BoxSizer(wx.VERTICAL)
        column_sizer.Add(self.column_c, 1, wx.EXPAND, 0)

        # Draw UI Elements
        self.ui.draw_lap_time_elements(self)
        self.ui.draw_lap_and_position_elements(self)

        # Re-size the screen as needed after elements are populated
        self.main_panel.SetSizer(main_sizer)
        self.Layout()

    def update(self, _):
        # Load a copy of the data so we know when it changes
        self.telemetry.load(dashboard_data.copy())

        # Ensure at least one packet has been parsed
        if len(dashboard_data.keys()) == 0 or not dashboard_data['active']:
            # Turn off any LEDs and stop logic
            self.led_controller.clear_status()
            return

        # Update LED Controller status
        self.led_controller.update_status()

        tire_temp = self.telemetry.tire_temperature
        # Tire Temp FL
        fl_tire = tire_temp['FL']
        self.tire_temp_FL.SetLabel(str(round(fl_tire['value'])))
        self.tire_temp_FL.SetForegroundColour(wx.Colour(fl_tire['color']))

        # Tire Temp FR
        fr_tire = tire_temp['FR']
        self.tire_temp_FR.SetLabel(str(round(fr_tire['value'])))
        self.tire_temp_FR.SetForegroundColour(wx.Colour(fr_tire['color']))

        # Tire Temp RL
        rl_tire = tire_temp['RL']
        self.tire_temp_RL.SetLabel(str(round(rl_tire['value'])))
        self.tire_temp_RL.SetForegroundColour(wx.Colour(rl_tire['color']))

        # Tire Temp RR
        rr_tire = tire_temp['RR']
        self.tire_temp_RR.SetLabel(str(round(rr_tire['value'])))
        self.tire_temp_RR.SetForegroundColour(wx.Colour(rr_tire['color']))

        # Update Speed & Gear
        self.speed_value.SetLabel(str(dashboard_data['speed']))
        self.gear_num_value.SetLabel(str(self.telemetry.gear))

        # Update Fuel level values
        self.total_fuel_value.SetLabel(self.telemetry.fuel_level)
        self.fuel_per_lap_value.SetLabel(self.telemetry.fuel_percent_per_lap)

        # Set Lap Time/Time Gain
        self.lap_time_value.SetLabel(self.telemetry.lap_time)
        time_gain = self.telemetry.time_gain
        self.time_gain_value.SetLabel(time_gain['value'])
        self.time_gain_value.SetForegroundColour(time_gain['color'])

        # Set Lap Number & Position
        self.lap_num_value.SetLabel(str(dashboard_data['lap_num'] + 1))
        self.position_value.SetLabel(str(dashboard_data['race_position']))

    def _start_timer(self, update_in_ms = 50):
        '''Start the update timer to refresh values on the UI'''
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.timer.Start(update_in_ms)

    def _set_window_properties(self):
        '''Set the core window properties such as title, size, background, etc.'''
        self.SetSize((800, 480))
        self.SetMinSize((800, 480))
        self.SetTitle("Dashboard GUI")
        self.SetBackgroundColour(wx.Colour(0, 0, 0))

class DashboardApp(wx.App):
    maximized = True

    # OnInit is called after wx.App.__init__ is finished
    def OnInit(self):
        # Create the main dashboard frame
        self.dashboard_frame = DashboardFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.dashboard_frame)

        # Show the frame and full-screen it by default
        self.dashboard_frame.Show()
        self.dashboard_frame.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)

        # Bind to the KEY_DOWN event for keyboard shortcuts
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

        # wx requires we return a bool from our OnInit method
        return True

    def _on_key_down(self, event):
        # Get the key code for the key pressed
        key_code = self._get_key_code(event)

        # Clear stints
        if key_code == wx.WXK_F10:
            self.dashboard_frame.telemetry.clear_stints()
        # Full-screen
        if key_code == wx.WXK_F11:
            self.maximized = not self.maximized
            self.dashboard_frame.ShowFullScreen(self.maximized, style=wx.FULLSCREEN_ALL)
        # Exiting
        elif key_code == wx.WXK_ESCAPE:
            self.dashboard_frame.Close()
            worker_process.terminate()
            exit(0)

    def _get_key_code(self, event):
        # Printable characters
        key_code = event.GetUnicodeKey()
        if key_code != wx.WXK_NONE:
            return key_code
        # Special characters
        return event.GetKeyCode()

with Manager() as manager:
    # Create shared dict for the worker and UI to use
    dashboard_data = manager.dict({})

    # Create the base app
    app = DashboardApp()

    # Load the configuration for the worker
    if not path.isfile('config.json'):
        raise Exception('config.json file is missing - please follow setup instructions.')
    with open("config.json", "r") as f:
        config = load(f)

    # Start the background worker process
    args = (dashboard_data, config['version'], config['host'], config['port'])
    worker_process = Process(target=worker, args=args)
    worker_process.start()

    # Run the main wx loop
    app.MainLoop()
