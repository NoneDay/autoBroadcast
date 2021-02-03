import sys, os
#sys.path.append(os.path.realpath(os.curdir))
from . import he_nan

def get(data_from,cookies):
    return he_nan.HeNan(data_from,cookies)