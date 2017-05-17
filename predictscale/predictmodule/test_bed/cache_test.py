import pandas as pd


def cache_training(data):
    data.to_csv('train.csv', header=False, index=False)


def cache(predictval, meanval, maxval):
    df = pd.DataFrame([[real, predictval, meanval, maxval]])
    df.to_csv('realtime.csv', header=False, index=False, mode='a')


def cache_real(real_val):
    df = pd.DataFrame([real_val, ])
    df.to_csv('realtime.origin.csv', header=False, index=False, mode='a')
