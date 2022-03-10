import adafruit_ahtx0
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
import traceback

# Setup I2C Sensor
sensor = adafruit_ahtx0.AHTx0(board.I2C())

# Convert Celsius to Fahrenheit
def c_to_f(input):
    return (input * 9 / 5) + 32

# Convert to two decimal places cleanly
# round() won't include trailing zeroes
def round_num(input):
    return '{:.2f}'.format(input)

# Save climate information locally
def save_entry(location, temperature, humidity):
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
        'humidity': sum(float(e['humidity']) for e in events) / len(events)
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

    # Use the same DF for both, but rename the subject field as needed
    return {
        'temperature': df.rename(columns={'temperature': 'value'}),
        'humidity': df.rename(columns={'humidity': 'value'})
    }

# Plot dataset on a axis with it's display information
def plot_data(data, ax, x_label, y_label, color, alpha = 1):
    color = 'tab:{}'.format(color)

    # Set labels
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label, color=color)
    ax.tick_params(axis='y', labelcolor=color)

    # Plot data
    ax.plot(data.index, data.value, marker='o', color=color, alpha=alpha)

@click.group()
def cli():
    pass

@cli.command()
@click.option('--chart-path', required=True, help='Path to store chart at')
@click.option('--location', required=True, help='Which entry location to export climate information for')
def export(chart_path, location):
    # Ensure the entries.json file is not missing
    if not os.path.isfile('entries.json'):
        print('Error: entries.json file is missing, please run the collect command first.')
        sys.exit(1)

    # Load entries from JSON file and convert to DataFrames
    data = get_entries(location)

    # Create the figure and both y-axes
    fig, ax1 = plt.subplots(figsize=(10, 8))
    ax2 = ax1.twinx()

    # Plot the data on two separate y-axes
    plot_data(data['temperature'], ax1, 'Date', 'Temperature (F)', 'red')
    plot_data(data['humidity'], ax2, 'Date', 'Humidity %', 'blue', 0.33)

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
    # Collect data and convert/round
    temperature = round_num(c_to_f(sensor.temperature))
    humidity = round_num(sensor.relative_humidity)

    # Save entry
    try:
        save_entry(location, temperature, humidity)
    except:
        # Print error traceback
        print(traceback.format_exc())
        sys.exit(1)

    print('Entry saved:', temperature, 'F,', humidity, '% H')

if __name__ == '__main__':
    cli()
