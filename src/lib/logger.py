import logging
import os


class logger():
    class __impl:
        """ Implementation of the singleton interface """

        # Default config values
        logger = None
        verbose = False
        debuglevel = 0

        def spam(self):
            """ Test method, return singleton id """
            return id(self)

        def debug(self, msg):
            msg = 'DEBUG: %s' % msg
            if self.debuglevel >= 3:
                logging.debug(msg)
                if self.verbose:
                    print(msg)

        def info(self, msg):
            msg = 'INFO: %s' % msg
            if self.debuglevel >= 2:
                logging.info(msg)
                if self.verbose:
                    print(msg)

        def warning(self, msg):
            msg = 'WARNING: %s' % msg
            if self.debuglevel >= 1:
                logging.warning(msg)
                if self.verbose:
                    print(msg)

        def error(self, msg):
            msg = 'ERROR: %s' % msg
            if self.debuglevel >= 0:
                logging.error(msg)
                if self.verbose:
                    print(msg)

        def setVerbose(self, verbose):
            self.verbose = verbose

        def getVerbose(self):
            return self.verbose

        def setDebuglevel(self, debuglevel):
            self.debuglevel = debuglevel

        def getDebuglevel(self):
            return self.debuglevel

    # storage for the instance reference
    __instance = None

    def __init__(self, logfile=None):
        """ Create singleton instance """
        # Check whether we already have an instance
        if logger.__instance is None:
            # Create and remember instance
            logger.__instance = logger.__impl()

            if(logfile):  # pragma: no cover
                logdirectory = os.path.dirname(logfile)
                if not os.path.exists(logdirectory):
                    os.makedirs(logdirectory)
                logging.basicConfig(filename=logfile,
                                    level=logging.DEBUG,
                                    format='%(asctime)s %(message)s',
                                    datefmt='%b %d %H:%M:%S')

        # Store instance reference as the only member in the handle
        self.__dict__['_logger__instance'] = logger.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
