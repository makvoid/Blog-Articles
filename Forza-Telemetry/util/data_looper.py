from datetime import datetime as datetime
import gzip
from json import load
from mimetypes import MimeTypes
from os import path

class DataLooper():
    '''
        DataLooper - a class designed to infinitely loop a sample set of
        data. Supports JSON or GZip'd JSON files
    '''
    def __init__(self, file = 'sample-file.json.gz', data_rate_ms = 250):
        self.file = file
        self.data_rate = data_rate_ms
        file_mime = MimeTypes().guess_type(self.file)

        # Ensure the file passed is valid
        if not path.isfile(self.file):
            raise ValueError(f'Invalid file path: {self.file}')

        # Ensure a valid time delta is passed
        if self.data_rate <= 0:
            raise ValueError('Data rate must be greater than zero')

        # Ensure the file is json
        if file_mime[0] != 'application/json':
            raise Exception(f'Unsupported file type (must be json): {file_mime[0]}')

        # If the file has a secondary file extension, ensure it is gzip
        if file_mime[1] == 'gzip':
            # Drop the last extension (ex. test.json.gz -> test.json)
            uncompressed = '.'.join(file.split('.')[:-1])
            # Check if the file has not been decompressed yet
            if not path.isfile(uncompressed):
                self._decompress_data(uncompressed)
            self.file = uncompressed
        # Otherwise, if it has one that is not gzip, fail
        elif file_mime[1] != None:
            raise Exception(f'Unsupported file type (must be gz/gzip): {file_mime[1]}')

        # Load and parse the data from the file
        self._load_data_from_file()

    def __iter__(self):
        '''Convert the class into an infinite iterable'''
        index = 0
        last = datetime.now()
        # Loop infinitely through the rows
        while True:
            delta = datetime.now() - last
            # If we are at or past our requested rate, return a value
            if delta.total_seconds() * 1000 >= self.data_rate:
                yield self.data[index]
                # Set the index for the next iteration
                if index + 1 == self._data_length:
                    index = 0
                else:
                    index += 1
                last = datetime.now()

    def _load_data_from_file(self):
        '''Load the requested file and parse the JSON'''
        with open(self.file, 'r') as f:
            self.data = load(f)
        self._data_length = len(self.data)

    def _decompress_data(self, target):
        '''Gunzip an archive into the uncompressed format'''
        with gzip.open(self.file, 'rb') as compressed:
            with open(target, 'wb') as f:
                f.write(compressed.read())
