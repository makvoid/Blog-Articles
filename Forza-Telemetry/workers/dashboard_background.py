import os
import socket
import sys

# Add the parent directory to our path
sys.path.append(os.path.abspath('..'))

from util.data_packet import DataPacket

# Handles the execution of receiving/parsing to leave
# the wx process unblocked
def worker(dashboard_data, game_version, host, port):
    # Create an ipv4 datagram-based socket and bind
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    # Instantiate class and variables
    dp = DataPacket(version=game_version)

    # Loop indefinitely until finished
    while True:
        # Receive a data packet from Forza
        packet, _ = sock.recvfrom(1024)

        # Parse this packet
        dp.parse(packet)

        # Update the shared dict of values - we cannot just
        # re-assign here as it won't detect the change
        for k, v in dp.to_dict().items():
            dashboard_data[k] = v

    # If the loop exits, close the socket if necessary
    sock.close()
