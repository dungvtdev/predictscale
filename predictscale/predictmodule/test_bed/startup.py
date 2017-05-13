import sys
import os

curpath = os.path.dirname(__file__)
predictmodule_path = os.path.dirname(curpath)
predictscale = os.path.dirname(predictmodule_path)

path = os.path.abspath(predictscale)
sys.path.append(path)
