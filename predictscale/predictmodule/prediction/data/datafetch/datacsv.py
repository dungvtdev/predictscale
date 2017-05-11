import pandas as pd


class CSVReader():

    def __init__(self, file_path):
        self.file_path = file_path

    def read(self):
        data = pd.read_csv(self.file_path, header=None)
        return data[0]

    def fetch_series(self):
        return self.read()
