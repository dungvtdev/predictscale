import requests
import pandas as pd

db_name = 'cadvisorxx'
ip = '192.168.122.124'
file = '1m.data.csv'


class FakeDataSource():
    def __init__(self):
        self.minute = 24916683
        self.pointer = 0
        series = pd.read_csv(file, header=None)
        series = series[0].interpolate()
        self.series = series
        self.max = len(series)

    def make_query(self):
        tmpl = 'http://{ip}:8086/write?db={db_name}'
        return tmpl.format(ip=ip, db_name=db_name)

    def push(self, loop_minute):
        if self.pointer >= self.max:
            return
        self.pointer = self.pointer + 1
        value = self.series[self.pointer]

        self.minute = self.minute + loop_minute
        t = self.minute * 60 * 1000000000
        s = 'cpu_usage_total,container_name=cpu_usage_total value={value} {time}'
        s = s.format(value=value, time=t)
        url = self.make_query()
        r = requests.post(url, data=s)


if __name__ == '__main__':
    fd = FakeDataSource()
    for i in range(200):
        fd.push(1)
