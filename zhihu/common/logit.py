from functools import wraps
from datetime import datetime

from zhihu.settings import LOG_FIEL

class logit():

    def __init__(self,logfile=LOG_FIEL):
        self.logfile = logfile

    def __call__(self,func):
        @wraps(func)
        def wraps_func(*args, **kwargs):
            log_string = "[" + str(datetime.now()) + "]" + " " + func.__name__ + " " + "was called"
            with open(self.logfile,"a") as f:
                f.write(log_string + "\n")

            return func(*args, **kwargs)

        return wraps_func



        