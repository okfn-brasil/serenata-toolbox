import logging
import os
import sys


LEVEL = logging.DEBUG if os.environ.get('DEBUG') else logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


# get a default logger to the project
log = logging.getLogger()
log.setLevel(LEVEL)

# make this log send messages to stdout
output = logging.StreamHandler(sys.stdout)
output.setLevel(LEVEL)
output.setFormatter(logging.Formatter(LOG_FORMAT))
log.addHandler(output)
