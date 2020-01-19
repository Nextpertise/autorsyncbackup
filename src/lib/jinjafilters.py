import datetime
import re

from jinja2 import Markup


class jinjafilters():
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

    def _epochToStrDate(self, epoch, strftime):
        if epoch:
            return datetime.datetime.fromtimestamp(epoch).strftime(strftime)

    def _bytesToReadableStr(self, byte_data):
        try:
            byte_data = float(byte_data)
        except Exception:
            byte_data = 0
        i = 0
        byteUnits = [' Bytes',
                     ' KB',
                     ' MB',
                     ' GB',
                     ' TB',
                     ' PB',
                     ' EB',
                     ' ZB',
                     ' YB']
        bytesStr = "%.0f" % byte_data
        while byte_data >= 1024:
            byte_data = byte_data / 1024
            i = i + 1
            bytesStr = "%.1f" % byte_data
        return bytesStr + byteUnits[i]

    def _secondsToReadableStr(self, seconds, short=False):
        try:
            seconds = int(seconds)
        except Exception:
            seconds = 0
        if seconds == 0:
            return "0 seconds"

        minutes = 0
        hours = 0
        days = 0
        weeks = 0

        while seconds >= 60:
            minutes += 1
            seconds -= 60

            if minutes == 60:
                hours += 1
                minutes = 0

                if hours == 24:
                    days += 1
                    hours = 0

                    if days == 7:
                        weeks += 1
                        days = 0

        ret = ""

        if weeks > 0:
            if ret != "":  # pragma: no cover
                ret += ", "

            if short:
                ret += "%s w" % weeks
            else:
                ret += "%s week" % weeks
                if weeks > 1:
                    ret += "s"

        if days > 0:
            if ret != "":  # pragma: no cover
                ret += ", "

            if short:
                ret += "%s d" % days
            else:
                ret += "%s day" % days
                if days > 1:
                    ret += "s"

        if hours > 0:
            if ret != "":  # pragma: no cover
                ret += ", "

            if short:
                ret += "%s h" % hours
            else:
                ret += "%s hour" % hours
                if hours > 1:
                    ret += "s"

        if minutes > 0:
            if ret != "":  # pragma: no cover
                ret += ", "

            if short:
                ret += "%s m" % minutes
            else:
                ret += "%s minute" % minutes
                if minutes > 1:
                    ret += "s"

        if seconds > 0:
            if ret != "":  # pragma: no cover
                ret += ", "

            if short:
                ret += "%s s" % seconds
            else:
                ret += "%s second" % seconds
                if seconds > 1:
                    ret += "s"

        return ret

    def _intToReadableStr(self, x):
        try:
            x = int(x)
        except Exception:
            x = 0
        if x < 0:
            return '-' + self._intToReadableStr(-x)
        result = ''
        while x >= 1000:
            x, r = divmod(x, 1000)
            result = ".%03d%s" % (r, result)
        return "%d%s" % (x, result)

    def _nl2br(self, value):
        result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n')
                              for p in self._paragraph_re.split(value))
        return Markup(result)
