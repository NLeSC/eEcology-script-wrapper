class SWException(Exception):
    pass

class TooManyDataPoints(SWException):
    pass

class NoDataPoints(SWException):
    pass

def validateDataPoints(count):
    if count > 1000000:
        raise TooManyDataPoints('Too many data points selected for this script, please reduce time range')
    if count == 0:
        raise NoDataPoints('No data points selected for this script, please increase or shift time range')
    return True