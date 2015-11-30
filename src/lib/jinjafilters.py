import datetime
from collections import OrderedDict

class jinjafilters():
    def _epochToStrDate(self, epoch, strftime):
        return datetime.datetime.fromtimestamp(epoch).strftime(strftime)
        
    def _bytesToReadableStr(self, bytes):
        try:
          bytes = float(bytes)
        except:
          bytes = 0
        i = 0
        byteUnits = [' Bytes', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB']
        bytesStr = "%.0f" % bytes
        while bytes > 1024:
            bytes = bytes / 1024
            i = i + 1
            bytesStr = "%.1f" % bytes
        return bytesStr + byteUnits[i]
        
    def _secondsToReadableStr(self, seconds, short=False):
        try:
          seconds = int(seconds)
        except:
          seconds = 0
        if seconds == 0:
            return "0 seconds"
        ret = ""
        if short:
            units = OrderedDict([('w', 7*24*3600), ('d', 24*3600), ('h', 3600), ('m', 60), ('s', 1)])
            space = ""
        else:
            units = OrderedDict([('week', 7*24*3600), ('day', 24*3600), ('hour', 3600), ('minute', 60), ('second', 1)])
            space = " "
        for unit in units:
            quot = seconds / units[unit]
            if quot:
               ret = ret + str(quot) + space + unit
               seconds = seconds - (quot * units[unit])
               if abs(quot) > 1:
                    if not short:
                        ret = ret + "s"
               ret = ret + ", "
        return ret[:-2]
        
    def _intToReadableStr(self, x):
        try:
            x = int(x)
        except:
            x = 0
        if x < 0:
            return '-' + _intToReadableStr(-x)
        result = ''
        while x >= 1000:
            x, r = divmod(x, 1000)
            result = ".%03d%s" % (r, result)
        return "%d%s" % (x, result)