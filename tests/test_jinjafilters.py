import datetime
import time


def test_epochToStrDate(filters):
    assert filters._epochToStrDate(None, None) is None

    epoch = time.time()
    format = "%Y-%m-%d %H:%M:%S"

    assert (filters._epochToStrDate(epoch, format) ==
            datetime.datetime.fromtimestamp(epoch).strftime(format))


def test_bytesToReadableStr(filters):
    assert filters._bytesToReadableStr('foo') == '0 Bytes'

    units = [
              'Bytes',
              'KB',
              'MB',
              'GB',
              'TB',
              'PB',
              'EB',
              'ZB',
              'YB',
            ]

    i = 0
    for unit in units:
        bytes = 1024 ** i

        if bytes < 1024:
            assert filters._bytesToReadableStr(bytes) == '1 %s' % units[i]
        else:
            assert filters._bytesToReadableStr(bytes) == '1.0 %s' % units[i]

        i += 1


def test_secondsToReadableStr(filters):
    assert filters._secondsToReadableStr('foo') == '0 seconds'

    assert filters._secondsToReadableStr(1.9) == '1 second'

    assert filters._secondsToReadableStr(265) == '4 minutes, 25 seconds'

    units = [
              {
                'short':   's',
                'long':    'second',
                'seconds': 1,
              },
              {
                'short':   'm',
                'long':    'minute',
                'seconds': 60,      # 1 * 60
              },
              {
                'short':   'h',
                'long':    'hour',
                'seconds': 3600,    # 60 * 60
              },
              {
                'short':   'd',
                'long':    'day',
                'seconds': 86400,   # 24 * (60 * 60)
              },
              {
                'short':   'w',
                'long':    'week',
                'seconds': 604800,  # 7 * (24 * (60 * 60))
              },
            ]

    for unit in units:
        seconds = 1 * unit['seconds']

        assert filters._secondsToReadableStr(seconds) == '1 %s' % unit['long']
        assert filters._secondsToReadableStr(seconds, True) == '1 %s' % (
                   unit['short'])

        seconds = 2 * unit['seconds']

        assert filters._secondsToReadableStr(seconds) == '2 %ss' % unit['long']
        assert filters._secondsToReadableStr(seconds, True) == '2 %s' % (
                   unit['short'])


def test_intToReadableStr(filters):
    assert filters._intToReadableStr('foo') == '0'

    assert filters._intToReadableStr(-1.9) == '-1'

    assert filters._intToReadableStr(8086) == '8.086'

    assert filters._intToReadableStr(314159) == '314.159'


def test_nl2br(filters):
    assert filters._nl2br('foo') == '<p>foo</p>'

    assert filters._nl2br('foo\n\nbar') == '<p>foo</p>\n\n<p>bar</p>'

    assert filters._nl2br('foo\n\nbar\nbaz') == ('<p>foo</p>\n\n'
                                                 '<p>bar<br>\nbaz</p>')
