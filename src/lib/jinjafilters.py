import datetime
import re
from collections import OrderedDict

from jinja2 import Markup

class jinjafilters():
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

    def _epochToStrDate(self, epoch, strftime):
        if epoch:
            return datetime.datetime.fromtimestamp(epoch).strftime(strftime)
        
    def _bytesToReadableStr(self, byte_data):
        try:
            byte_data = float(byte_data)
        except:
            byte_data = 0
        i = 0
        byteUnits = [' Bytes', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB', ' YB']
        bytesStr = "%.0f" % byte_data
        while byte_data > 1024:
            byte_data = byte_data / 1024
            i = i + 1
            bytesStr = "%.1f" % byte_data
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
            return '-' + self._intToReadableStr(-x)
        result = ''
        while x >= 1000:
            x, r = divmod(x, 1000)
            result = ".%03d%s" % (r, result)
        return "%d%s" % (x, result)

    def _nl2br(self, value):
        result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
            for p in self._paragraph_re.split(value))
        return Markup(result)
