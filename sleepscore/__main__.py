"""Sleepscore

Usage:
  sleepscore <config_path>

Options:
  -h --help      show this
"""


import sleepscore
from docopt import docopt


if __name__ == '__main__':

    args = docopt(__doc__)

    # Load config
    config_path = args['<config_path>']

    # Run main function
    sleepscore.run(config_path)
