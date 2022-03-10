import adafruit_ahtx0
import adafruit_sgp40
import board
import click
import datetime
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import pandas as pd
import pathlib
import sys
import time
import traceback

# Setup I2C Sensor
i2c = board.I2C()
aht = adafruit_ahtx0.AHTx0(i2c)
sgp = adafruit_sgp40.SGP40(i2c)

# Convert Celsius to Fahrenheit
def c_to_f(input):
    return (input * 9 / 5) + 32

# Convert to two decimal places cleanly
# round() won't include trailing zeroes
def round_num(input):
    return '{:.2f}'.format(input)

# Save climate information locally
def save_entry(location, temperature, humidity, aqi):
    # Ensure the file exists before attempting to read
    if not os.path.isfile('entries.json'):
        pathlib.Path('entries.json').touch(exist_ok=False)
        entries = []
    else:
        # Load any old entries
        with open("entries.json", "r") as f:
            try:
                entries = json.loads(f.read())
            except Exception as e:
                print('Error: Parsing entries.json failed')
                raise e

    # Add this new entry to the list
    entries.append({
        'location': location,
        'temperature': temperature,
        'humidity': humidity,
        'aqi': aqi,
        'date': datetime.datetime.now().isoformat()
    })

    # Save the list
    with open("entries.json", "w") as f:
        try:
            f.write(json.dumps(entries, indent=2))
        except Exception as e:
            print('Error: Saving entries.json failed')
            raise e

def average_date(date, entries):
    # Get a list of all entries for this date
    events = list(filter(lambda x: (x['date'][0:10] == date), entries))
    return {
        'date': pd.to_datetime(date),
        'temperature': sum(float(e['temperature']) for e in events) / len(events),
        'humidity': sum(float(e['humidity']) for e in events) / len(events),
        'aqi': sum(e['aqi'] for e in events) / len(events)
    }

# Returns entries as DataFrames
def get_entries(location):
    # load entries from file
    with open("entries.json", "r") as f:
        all_entries = json.loads(f.read())

    # Filter entries by our location
    entries = list(filter(lambda e: e['location'] == location, all_entries))

    # Ensure at least one entry is returned for this location
    if len(entries) == 0:
        print('Error: No entries found for location ({}). Try another?'.format(location))
        sys.exit(1)

    # Get a set/list of unique dates in YYYY-MM-DD format from the entries
    dates = set(map(lambda e: e['date'][0:10], entries))

    # Get the average temperature and humidity per day and convert to a DataFrame
    df = pd.DataFrame(map(lambda date: average_date(date, entries), dates))

    # Sort values by the date and set it as the index
    df = df.sort_values('date', ascending=True).set_index('date')

    return df

# Plot dataset on a axis with it's display information
def plot_data(data, field, ax, x_label, y_label, color, alpha = 1):
    color = 'tab:{}'.format(color)

    # Set labels
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label, color=color)
    ax.tick_params(axis='y', labelcolor=color)

    # Plot data
    ax.plot(data.index, data[field], marker='o', color=color, alpha=alpha)

# Measure index from sensor
def get_air_quality_index():
    return sgp.measure_index(aht.temperature, aht.relative_humidity)

# Return the time in milliseconds
def get_ms():
    return round(time.time() * 1000)

# Sample index readings over 3-minutes to ensure sensor was fully calibrated
def sample_air_quality_index():
    # Loop over each second in the range
    for x in range(180):
        start = get_ms()
        # Show an update every 30s
        if x % 30 == 0:
            print(f'{x}/180 - sampling still in progress, please wait...')
        # Sample the index for calibration
        get_air_quality_index()
        # Only sleep for what time remains in this iteration to achieve 1hz sampling
        time.sleep((1000 - (get_ms() - start)) / 1000)
    # After the sampling time frame, return a final reading
    return get_air_quality_index()

@click.group()
def cli():
    pass

@cli.command()
@click.option(
    '--chart-path',
    required=True,
    help='Path to store chart at'
)
@click.option(
    '--location',
    required=True,
    help='Which entry location to export information for'
)
@click.option(
    '--export-type',
    required=True,
    type=click.Choice(['climate', 'air-quality'], case_sensitive=False),
    help='Which data to export'
)
def export(chart_path, location, export_type):
    # Ensure the entries.json file is not missing
    if not os.path.isfile('entries.json'):
        print('Error: entries.json file is missing, please run the collect command first.')
        sys.exit(1)

    # Load entries from JSON file and convert to DataFrames
    data = get_entries(location)

    # Create the figure and initial axis
    fig, ax1 = plt.subplots(figsize=(10, 8))

    if export_type == 'climate':
        # Plot the data on two separate axes
        plot_data(data, 'temperature', ax1, 'Date', 'Temperature (F)', 'red')
        plot_data(data, 'humidity', ax1.twinx(), 'Date', 'Humidity %', 'blue', 0.33)
    else:
        # Plot the data on a separate chart for visibility
        plot_data(data, 'aqi', ax1, 'Date', 'Air Quality Index (AQI)', 'green')

    # Show the grid
    plt.grid()

    # Set the date and label formatter for the x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate()

    # Save the chart
    plt.savefig(chart_path)
    print('Chart saved to:', chart_path)

@cli.command()
@click.option('--location', required=True, help='Sensor location name')
def collect(location):
    # Sample the air quality index
    aqi = sample_air_quality_index()

    # Collect climate data and convert/round once AQI is calculated
    temperature = round_num(c_to_f(aht.temperature))
    humidity = round_num(aht.relative_humidity)

    # Save entry
    try:
        save_entry(location, temperature, humidity, aqi)
    except:
        # Print error traceback
        print(traceback.format_exc())
        sys.exit(1)

    print('Entry saved:', temperature, 'F,', humidity, '% H,', aqi, 'AQI')

if __name__ == '__main__':
    cli()
