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
        
    def _secondsToReadableStr(self, seconds):
        try:
          seconds = int(seconds)
        except:
          seconds = 0
        if seconds == 0:
            return "0 seconds"
        ret = ""
        units = OrderedDict([('week', 7*24*3600), ('day', 24*3600), ('hour', 3600), ('minute', 60), ('second', 1)])
        for unit in units:
            quot = seconds / units[unit]
            if quot:
               ret = ret + str(quot) + " " + unit
               seconds = seconds - (quot * units[unit])
               if abs(quot) > 1:
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