import startup
from predictmodule.algorithm.datafeeder.base import BaseFeeder


feeder = BaseFeeder(n_input=4, n_periodic=1, period=6)

data = range(100)
extend = range(5)

rl = feeder.generate_extend(data, extend)
print(rl)
