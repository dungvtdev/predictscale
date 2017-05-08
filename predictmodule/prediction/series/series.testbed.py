import base as series


def test_minute():
    s = series.SeriesMinute()
    s.append([1, 2, 3], 3)
    s.append([2, 3, 4, 5, ], 5)
    s.append([7, ], 7)
    print(s.data)


def test_secs():
    d1 = [
        (1494254560, 1),
        (1494254600, 2),
        (1494254630, 3),
        (1494254640, 4),
        (1494254780, 5),
        (1494254819, 3),
    ]

    s = series.SeriesMinute()
    s.append_secs(d1)
    print(s.data)
    print(s.last_secs)

test_minute()
test_secs()
