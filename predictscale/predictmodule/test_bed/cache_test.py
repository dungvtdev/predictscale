import pandas as pd


def cache_training(instance_id, data):
    data.to_csv('train-{name}.csv'.format(name=instance_id),
                header=False, index=False)


def cache(instance_id, val_list):  # predictval, meanval, maxval):
    predictval = val_list[0]
    meanval = val_list[1]
    maxval = val_list[2]
    df = pd.DataFrame([[predictval, meanval, maxval]])
    df.to_csv('realtime-{name}.csv'.format(name=instance_id),
              header=False, index=False, mode='a')


def cache_real(instance_id, real_val):
    df = pd.DataFrame([real_val, ])
    df.to_csv('realtime.origin-{name}.csv'.format(name=instance_id),
              header=False, index=False, mode='a')
