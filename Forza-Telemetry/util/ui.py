import wx

class UIElements():
    def draw_tire_temperature_elements(self, frame):
        '''Draw all four tires temperature elements'''
        # Create vertical sizer box to hold the elements
        tire_temp_sizer = wx.BoxSizer(wx.VERTICAL)
        frame.column_a.Add(tire_temp_sizer, 1, wx.EXPAND, 0)

        # Create a padding at the top for spacing
        spacer = wx.StaticText(frame.main_panel, wx.ID_ANY, "\n")
        spacer.SetMinSize((1, 20))
        tire_temp_sizer.Add(spacer, 0, wx.ALL, 0)

        # Create the display label
        tire_temp_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "TIRE TEMP")
        tire_temp_label.SetForegroundColour(wx.Colour(255, 255, 255))
        tire_temp_label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        tire_temp_sizer.Add(tire_temp_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Create a horizontal sizer box to hold the FL & FR values
        tire_temp_row_1 = wx.BoxSizer(wx.HORIZONTAL)
        tire_temp_sizer.Add(tire_temp_row_1, 1, wx.EXPAND, 0)

        # Create the FL label
        frame.tire_temp_FL = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.tire_temp_FL.SetMinSize((115, 39))
        frame.tire_temp_FL.SetForegroundColour(wx.Colour(127, 255, 0))
        frame.tire_temp_FL.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        tire_temp_row_1.Add(frame.tire_temp_FL, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        # Create the FR label
        frame.tire_temp_FR = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.tire_temp_FR.SetMinSize((100, 39))
        frame.tire_temp_FR.SetForegroundColour(wx.Colour(127, 255, 0))
        frame.tire_temp_FR.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        tire_temp_row_1.Add(frame.tire_temp_FR, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        # Create a horizontal sizer box to hold the RL & RR values
        tire_temp_row_2 = wx.BoxSizer(wx.HORIZONTAL)
        tire_temp_sizer.Add(tire_temp_row_2, 1, wx.EXPAND, 0)

        # Create the RL label
        frame.tire_temp_RL = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.tire_temp_RL.SetMinSize((115, 39))
        frame.tire_temp_RL.SetForegroundColour(wx.Colour(127, 255, 0))
        frame.tire_temp_RL.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        tire_temp_row_2.Add(frame.tire_temp_RL, 0, wx.ALL, 10)

        # Create the RR label
        frame.tire_temp_RR = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.tire_temp_RR.SetMinSize((100, 39))
        frame.tire_temp_RR.SetForegroundColour(wx.Colour(127, 255, 0))
        frame.tire_temp_RR.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        tire_temp_row_2.Add(frame.tire_temp_RR, 0, wx.ALL, 10)

    def draw_fuel_elements(self, frame):
        '''Draw the fuel elements'''
        # Add a spacer to separate tire temperature and fuel values
        fuel_sizer = wx.BoxSizer(wx.VERTICAL)
        frame.column_a.Add(fuel_sizer, 1, wx.EXPAND, 0)

        # Create the display label for total fuel
        total_fuel_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "TOTAL FUEL")
        total_fuel_label.SetForegroundColour(wx.Colour(255, 255, 255))
        total_fuel_label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        fuel_sizer.Add(total_fuel_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Create the value label for total fuel
        frame.total_fuel_value = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.total_fuel_value.SetForegroundColour(wx.Colour(255, 255, 0))
        frame.total_fuel_value.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        fuel_sizer.Add(frame.total_fuel_value, 0, wx.EXPAND | wx.ALL, 5)

        # Add a spacer to separete the content
        spacer = wx.StaticText(frame.main_panel, wx.ID_ANY, "\n")
        spacer.SetMinSize((1, 30))
        fuel_sizer.Add(spacer, 0, wx.ALL, 0)

        # Create the display label for fuel % per lap
        fuel_per_lap_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "FUEL % / LAP")
        fuel_per_lap_label.SetForegroundColour(wx.Colour(255, 255, 255))
        fuel_per_lap_label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        fuel_sizer.Add(fuel_per_lap_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Create the value label for fuel % per lap
        frame.fuel_per_lap_value = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.fuel_per_lap_value.SetForegroundColour(wx.Colour(255, 255, 0))
        frame.fuel_per_lap_value.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        fuel_sizer.Add(frame.fuel_per_lap_value, 0, wx.EXPAND | wx.ALL, 5)

    def draw_gear_and_speed_elements(self, frame):
        '''Draw the gear and speed elements'''
        # Add a vertical sizer to hold both sections
        gear_speed_sizer = wx.BoxSizer(wx.VERTICAL)
        frame.column_b.Add(gear_speed_sizer, 1, wx.EXPAND, 0)

        # Create a vertical sizer to hold the gear elements
        gear_sizer = wx.BoxSizer(wx.VERTICAL)
        gear_speed_sizer.Add(gear_sizer, 1, wx.EXPAND, 0)

        # Create a spacer for padding at the top
        spacer = wx.StaticText(frame.main_panel, wx.ID_ANY, "\n")
        spacer.SetMinSize((1, 20))
        gear_sizer.Add(spacer, 0, wx.ALL, 0)

        # Create the gear display label
        gear_num_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "GEAR")
        gear_num_label.SetForegroundColour(wx.Colour(255, 255, 255))
        gear_num_label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        gear_sizer.Add(gear_num_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Create the value label for gear number
        frame.gear_num_value = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.gear_num_value.SetForegroundColour(wx.Colour(255, 255, 0))
        frame.gear_num_value.SetFont(wx.Font(100, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        gear_sizer.Add(frame.gear_num_value, 0, wx.EXPAND, 0)

        # Create a vertical sizer to hold the speed elements
        speed_sizer = wx.BoxSizer(wx.VERTICAL)
        gear_speed_sizer.Add(speed_sizer, 1, wx.EXPAND, 0)

        # Create the display label
        speed_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "SPEED")
        speed_label.SetForegroundColour(wx.Colour(255, 255, 255))
        speed_label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        speed_sizer.Add(speed_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Create the speed value label
        frame.speed_value = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.speed_value.SetForegroundColour(wx.Colour(255, 255, 0))
        frame.speed_value.SetMinSize((211, 117))
        frame.speed_value.SetFont(wx.Font(75, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        speed_sizer.Add(frame.speed_value, 0, wx.EXPAND, 0)

    def draw_lap_time_elements(self, frame):
        '''Draw the lap time and time gain elements'''
        # Create a spacer for padding at the top
        spacer = wx.StaticText(frame.main_panel, wx.ID_ANY, "\n")
        spacer.SetMinSize((1, 20))
        frame.column_c.Add(spacer, 0, wx.ALL, 0)

        # Create the lap time display label
        lap_time_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "LAP TIME")
        lap_time_label.SetForegroundColour(wx.Colour(255, 255, 255))
        lap_time_label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        frame.column_c.Add(lap_time_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Create the lap time value label
        frame.lap_time_value = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.lap_time_value.SetForegroundColour(wx.Colour(255, 255, 0))
        frame.lap_time_value.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        frame.column_c.Add(frame.lap_time_value, 0, wx.EXPAND, 5)

        # Create a spacer to separate the values
        spacer = wx.StaticText(frame.main_panel, wx.ID_ANY, "\n")
        spacer.SetMinSize((1, 20))
        frame.column_c.Add(spacer, 0, wx.ALL, 0)

        # Create the time gain display label
        time_gain_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "TIME GAIN")
        time_gain_label.SetForegroundColour(wx.Colour(255, 255, 255))
        time_gain_label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        frame.column_c.Add(time_gain_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Create the time gain value label
        frame.time_gain_value = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.time_gain_value.SetForegroundColour(wx.Colour(255, 255, 0))
        frame.time_gain_value.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        frame.column_c.Add(frame.time_gain_value, 0, wx.EXPAND, 5)

    def draw_lap_and_position_elements(self, frame):
        '''Draw the lap and race position elements'''
        # Create a spacer to separate the values
        spacer_2_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "\n")
        spacer_2_label.SetMinSize((1, 40))
        frame.column_c.Add(spacer_2_label, 0, wx.ALL, 0)

        # Create the lap number display label
        lap_num_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "LAP #", style=wx.ALIGN_CENTER_HORIZONTAL)
        lap_num_label.SetForegroundColour(wx.Colour(255, 255, 255))
        lap_num_label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        frame.column_c.Add(lap_num_label, 0, wx.EXPAND | wx.ALL, 5)

        # Create the lap number value label
        frame.lap_num_value = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.lap_num_value.SetForegroundColour(wx.Colour(255, 255, 0))
        frame.lap_num_value.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        frame.column_c.Add(frame.lap_num_value, 0, wx.EXPAND, 5)

        # Create a spacer to separate the values
        spacer_3_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "\n")
        spacer_3_label.SetMinSize((1, 40))
        frame.column_c.Add(spacer_3_label, 0, wx.ALL, 0)

        # Create the position display label
        position_label = wx.StaticText(frame.main_panel, wx.ID_ANY, "POSITION")
        position_label.SetForegroundColour(wx.Colour(255, 255, 255))
        position_label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
        frame.column_c.Add(position_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Create the position value label
        frame.position_value = wx.StaticText(frame.main_panel, wx.ID_ANY, "-", style=wx.ST_NO_AUTORESIZE | wx.ALIGN_CENTER_HORIZONTAL)
        frame.position_value.SetForegroundColour(wx.Colour(255, 255, 0))
        frame.position_value.SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
        frame.column_c.Add(frame.position_value, 0, wx.EXPAND, 5)
