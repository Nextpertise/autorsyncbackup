import logging, os

class logger():
    class __impl:
        """ Implementation of the singleton interface """
        
        # Default config values
        logger = None

        def spam(self):
            """ Test method, return singleton id """
            return id(self)
        
        def debug(self, msg):
            logging.debug(msg)
            
        def info(self, msg):
            logging.info(msg)
            
        def warning(self, msg):
            logging.warning(msg)
            
        def error(self, msg):
            logging.error(msg)

    # storage for the instance reference
    __instance = None
    
    def __init__(self, logfile=None):
        """ Create singleton instance """
        # Check whether we already have an instance
        if logger.__instance is None:
            # Create and remember instance
            logger.__instance = logger.__impl()
            
            if(logfile):
                logdirectory = os.path.dirname(logfile)
                if not os.path.exists(logdirectory):
                    os.makedirs(logdirectory)
                logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%b %d %H:%M:%S')

        # Store instance reference as the only member in the handle
        self.__dict__['_logger__instance'] = logger.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
