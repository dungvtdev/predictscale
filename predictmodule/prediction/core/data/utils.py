import pandas as pd


def time_series_to_pandas_series_minute(time_series, interpolate=False):
    df = time_series if isinstance(time_series, pd.DataFrame) \
        else pd.DataFrame(time_series)
    convert = 1000000000 * 60
    df = df.set_index(pd.to_datetime(df[0] * convert))[1]
    df = df.resample('T').mean()
    if interpolate:
        interpolate_pandas_time_series(df)
    return df


def interpolate_pandas_time_series(series):
    return series.interpolate()
