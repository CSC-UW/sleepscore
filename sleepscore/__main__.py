"""Sleepscore

Usage:
  sleepscore <config_path>

Options:
  -h --help      show this
"""


import sleepscore
import yaml
from docopt import docopt


if __name__ == '__main__':

    args = docopt(__doc__)

    # Load config
    config_path = args['<config_path>']
    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    print(f"Sleepscore config: \n Path={config_path}, \n Config={config}, \n")

    sleepscore.load_and_score(
        config['binPath'],
        datatype=config['datatype'],
        downSample=config['downSample'],
        tStart=config['tStart'],
        tEnd=config['tEnd'],
        chanList=config['chanList'],
        chanListType=config['chanListType'],
        chanLabelsMap=config['chanLabelsMap'],
        unit=config['unit'],
        kwargs_sleep=config['kwargs_sleep'],
    )
