import base as series

s = series.SeriesMinute()

s.append([1, 2, 3], 3)

s.append([2, 3, 4, 5, ], 5)

s.append([7, ], 7)

print(s.data)
