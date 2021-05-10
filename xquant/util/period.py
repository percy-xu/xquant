import datetime
import pandas as pd
from typing import Union
from xquant.util import check_time

class Period():
    '''
    Period
    ------
    A simple class that represents a time period with a start time and end time

    Parameters
    ----------
    start_time: a datetime.datetime object
    end_time = None: a datetime.datetime object later than start_time
    duration = None: a datetime.timedelta object

    One of end_time or duration must be provided
    '''
    def __init__(self, start_time, end_time=None, duration=None) -> None:
        # make sure end_time is later than start_time
        if end_time != None:
            assert (end_time - start_time).total_seconds() > 0
            assert duration == None
            duration = end_time - start_time
        else:
            assert duration.total_seconds() > 0
            end_time = start_time + duration

        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration

    def contains_time(self, time:Union[datetime.datetime, pd.Timestamp]) -> bool:
        '''checks if a time is within a period'''
        assert check_time(time=time)
        if self.start_time <= time <= self.end_time:
            return True
        else:
            return False

if __name__ == '__main__':
    pass