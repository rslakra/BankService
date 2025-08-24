import logging

# Configure app default loggers
logging.basicConfig(level=logging.DEBUG,
                    format="[%(asctime)s] [%(process)d] [%(levelname)s] - %(message)s",
                    force=True)


def getLogger(name=__name__):
    """Return the logger for the given file"""
    return logging.getLogger(name)
