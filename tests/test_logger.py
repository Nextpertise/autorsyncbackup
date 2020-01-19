import re

from lib.logger import logger


def test_logger_verbose():
    logger().verbose = False

    assert logger().getVerbose() is False
    assert logger().verbose is False

    logger().setVerbose(True)

    assert logger().getVerbose() is True
    assert logger().verbose is True


def test_debuglevel():
    logger().debuglevel = 0

    assert logger().getDebuglevel() == 0
    assert logger().debuglevel == 0

    logger().setDebuglevel(3)

    assert logger().getDebuglevel() == 3
    assert logger().debuglevel == 3


def test_debug(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = True
    logger().debuglevel = 3

    message = 'Debug Message'

    logger().debug(message)

    captured = capsys.readouterr()

    assert "DEBUG: %s" % message in captured.out

    logger().debuglevel = debuglevel


def test_debug_no_verbose(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = False
    logger().debuglevel = 3

    message = 'Second Debug Message'

    logger().debug(message)

    captured = capsys.readouterr()

    assert "DEBUG: %s" % message not in captured.out

    logger().debuglevel = debuglevel


def test_debug_debuglevel(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = False
    logger().debuglevel = -1

    message = 'Third Debug Message'

    logger().debug(message)

    captured = capsys.readouterr()

    assert "DEBUG: %s" % message not in captured.out

    logger().debuglevel = debuglevel


def test_info(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = True
    logger().debuglevel = 2

    message = 'Info Message'

    logger().info(message)

    captured = capsys.readouterr()

    assert "INFO: %s" % message in captured.out

    logger().debuglevel = debuglevel


def test_info_no_verbose(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = False
    logger().debuglevel = 2

    message = 'Second Info Message'

    logger().info(message)

    captured = capsys.readouterr()

    assert "INFO: %s" % message not in captured.out

    logger().debuglevel = debuglevel


def test_info_debuglevel(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = False
    logger().debuglevel = -1

    message = 'Third Info Message'

    logger().info(message)

    captured = capsys.readouterr()

    assert "INFO: %s" % message not in captured.out

    logger().debuglevel = debuglevel


def test_warning(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = True
    logger().debuglevel = 1

    message = 'Warning Message'

    logger().warning(message)

    captured = capsys.readouterr()

    assert "WARNING: %s" % message in captured.out

    logger().debuglevel = debuglevel


def test_warning_no_verbose(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = False
    logger().debuglevel = 1

    message = 'Second Warning Message'

    logger().warning(message)

    captured = capsys.readouterr()

    assert "WARNING: %s" % message not in captured.out

    logger().debuglevel = debuglevel


def test_warning_debuglevel(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = False
    logger().debuglevel = -1

    message = 'Third Warning Message'

    logger().warning(message)

    captured = capsys.readouterr()

    assert "WARNING: %s" % message not in captured.out

    logger().debuglevel = debuglevel


def test_error(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = True
    logger().debuglevel = 0

    message = 'Error Message'

    logger().error(message)

    captured = capsys.readouterr()

    assert "ERROR: %s" % message in captured.out

    logger().debuglevel = debuglevel


def test_error_no_verbose(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = False
    logger().debuglevel = 0

    message = 'Second Error Message'

    logger().error(message)

    captured = capsys.readouterr()

    assert "ERROR: %s" % message not in captured.out

    logger().debuglevel = debuglevel


def test_error_debuglevel(capsys):
    debuglevel = logger().debuglevel

    logger().verbose = False
    logger().debuglevel = -1

    message = 'Third Error Message'

    logger().error(message)

    captured = capsys.readouterr()

    assert "ERROR: %s" % message not in captured.out

    logger().debuglevel = debuglevel


def test_spam():
    assert re.match(r'^\d+$', str(logger().spam()))


def test_attr():
    assert logger().__setattr__('verbose', False) is None

    assert logger().__getattr__('verbose') is False
