import click
import gzip
from json import dumps
from multiprocessing import Manager, Process
import socket
from struct import pack
from yaspin import yaspin

from util.data_looper import DataLooper
from util.data_packet import DataPacket
from workers.recorder import worker

@click.group()
def cli():
    '''
        Recording and rebroadcasting tools for working with
        Forza Data Packets.
    '''

@cli.command()
@click.option(
    '--game-version',
    required=True,
    type=click.Choice(['sled', 'dash', 'fh4+'], case_sensitive=False),
    help='Version of the Telemetry to receive packets for'
)
@click.option(
    '--file-path',
    required=True,
    help='Path to save the data recording at (ex. recording.json.gz - must be of .json.gz extension)'
)
@click.option(
    '--host',
    default='0.0.0.0',
    help='Address to bind recorder to (ex 127.0.0.1)'
)
@click.option(
    '--port',
    default=5555,
    type=int,
    help='Port to bind recorder to (ex. 5555)'
)
def record(game_version, file_path, host, port):
    '''
        Easily record Forza Data Packets into compressed JSON files so that they
        can be reported off of or rebroadcasted at a later date.
    '''
    # Check the file extension provided
    if '.'.join(file_path.split('.')[-2:]) != 'json.gz':
        raise Exception(f"File name must be prepended with '.json.gz': {file_path}")

    with Manager() as manager:
        # Create a shared list and a worker process to handle the actual recording
        packets = manager.list()
        p = Process(target=worker, args=(packets, game_version, host, port,))
        p.start()

        # Wait for the worker to start and potentially error out
        p.join(0.1)
        if not p.is_alive():
            print('Error starting worker, most likely a data format issue is occurring.')
            return

        # Wait for the User to stop recording
        input('Press any key when you are ready to stop recording.')

        # Terminate the worker process if applicable
        try:
            p.terminate()
        except:
            pass

        # Ensure some data was recorded
        if len(packets) == 0:
            print('No data was recorded, not saving to a file.')
            return

        # Save the packets before closing the Manager (or we lose the values)
        with gzip.open(file_path, 'wb') as f:
            f.write(dumps(list(packets)).encode('utf-8'))

    print('Saved file to:', file_path)

@cli.command()
@click.option(
    '--game-version',
    required=True,
    type=click.Choice(['sled', 'dash', 'fh4+'], case_sensitive=False),
    help='Version of the Telemetry to generate packets for'
)
@click.option(
    '--host',
    required=True,
    help='Host where packets are being accepted (ex. 127.0.0.1)',
)
@click.option(
    '--port',
    required=True,
    type=int,
    help='Port where packets are being accepted (ex.5555)'
)
@click.option(
    '--rate',
    default=1000 / 60,
    help='Rate at which to send packets (in ms) - default: 16.6666 (1000 / 60 - 60hz)'
)
@click.option(
    '--input-file',
    required=True,
    help='Sample data use in the rebroadcast'
)
def rebroadcast(game_version, host, port, rate, input_file):
    '''
        Rebroadcast recorded Forza Data Packets to an endpoint at a specified
        rate. Recordings are backwards compatible, however, they are not forward
        compatible. You can record 'fh4+' packets and rebroadcast them for the
        'sled' packet type and the code will automatically truncate the data as
        needed, but for example you cannot use a 'sled' recording for the 'dash'
        game version as it is missing required fields.
    '''
    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set the format for the game version
    if game_version == 'sled':
        data_format = DataPacket._default_format
    elif game_version == 'dash':
        data_format = DataPacket._dash_format
    elif game_version == 'fh4+':
        data_format = DataPacket._horizon_format

    # Loop data until canceled
    packets_sent = 0
    with yaspin(color='green') as spinner:
        for row in DataLooper(input_file, rate):
            # Prevent older recordings being used on newer versions
            if game_version == 'dash':
                if len(row) == 58:
                    raise Exception('Data is of "sled" format but game version was set to "dash".')
            elif game_version == 'fh4+' and len(row) != 89:
                data_type = 'unknown'
                if len(row) == 58:
                    data_type = 'sled'
                elif len(row) == 85:
                    data_type = 'dash'
                raise Exception(f'Data is of type "{data_type}" but game version was set to "fh4+".')

            # Truncate the data as needed for older versions for backwards compatibility
            if len(row) == 89: # FH4+ field length
                if game_version == 'sled':
                    row = row[0:58]
                elif game_version == 'dash':
                    row = row[0:58] + row[61:88]

            # Send data packet
            sock.sendto(pack(data_format, *row), (host, port))
            packets_sent += 1
            spinner.text = f'{packets_sent:,} packets sent in total'

    # If the loop exits, close the socket if necessary
    sock.close()

if __name__ == '__main__':
    cli()