import os
import socket
import sys

# Add the parent directory to our path
sys.path.append(os.path.abspath('..'))

from util.data_packet import DataPacket

# Handles the execution of receiving/parsing to leave
# the main process unblocked
def worker(packets, game_version, host, port):
    # Create an ipv4 datagram-based socket and bind
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    # Instantiate class and variables
    dp = DataPacket(version=game_version)

    # Loop indefinitely until finished
    while True:
        # Receive a data packet from Forza
        packet, _ = sock.recvfrom(1024)

        # Parse this packet, however, don't convert values
        dp.parse(packet, recording = True)

        # Append this packet to the shared list
        packets.append(dp.to_dict().values())

    # If the loop exits, close the socket if necessary
    sock.close()