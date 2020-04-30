"""Load and sleepscore using visbrain.Sleep datasets in multiple formats."""

import warnings

import numpy as np

import EMGfromLFP
import yaml
from visbrain.gui import Sleep

from .load import loader_switch
from .validation import validate


def run(config_path):
    """Call `load_and_score` from config file.

    Mandatory and optional keys in the config file are the (resp.) args and
    kwargs of `sleepscore.load_and_score`. Refer to `sleepscore.load_and_score`
    for a description of expected parameters.
    """

    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    print(f"Sleepscore config: \n Path={config_path}, \n Config={config}, \n")

    # Validate
    # Check keys in config are the same as ``load_and_score`` args/kwargs and
    # set default values
    mandatory_keys = get_args(load_and_score)
    optional_keys = get_kwargs(load_and_score)
    config = validate(config, mandatory=mandatory_keys, optional=optional_keys,
                      prefix='Validating config dictionary: ')
    # Check USER didn't write "None" instead of yaml's "null"
    none_keys = [k for k, v in config.items()
                 if isinstance(v, str) and v.lower() == 'none']
    if none_keys:
        raise ValueError(
            f"Python's 'None' value should be written 'null' in yaml. Please"
            f" update your config file accordingly (check keys = {none_keys})"
        )

    # Call `load_and_score`
    mandatory = [config[k] for k in mandatory_keys]
    optional = {k: v for k, v in config.items() if k in optional_keys}
    load_and_score(*mandatory, **optional)


def load_and_score(datasets, downSample=100.0, tStart=None, tEnd=None,
                   EMGdatapath=None, kwargs_sleep={}):
    """Load data and run visbrain's Sleep.

    Args:
        datasets (list(dict)): List of dictionaries specifying the data to load.
            Each of the dictionaries specifies the data loaded from a specific
            dataset. For each of the dictionaries, the following keys are
            recognized:
                binPath (str | pathlib.Path): Path to bin of recording
                    (mandatory)
                datatype (str): 'SGLX' , 'TDT' or 'OpenEphys' (default 'SGLX')
                chanList (list(str) | None): List of loaded channels. All
                    channels are loaded by default. (default None)
                        - for SGLX data: `chanList` is interpreted
                            as labels of channels, eg::
                                ["LF0;384", "LF1;385"]
                        - for TDT data: Values in ChanList should be string
                            formatted as follows::
                                [<score_name>-<channel_index>, ...]
                            Where channels are 1-indexed, (IMPORTANT) not
                            0-indexed (for consistency with tdt methods), eg::
                                [LFPs-1, LFPs-2, EEGs-1, EEGs-94, EMGs-1]
                chanLabelsMap (dict | None): {<channel>: <new_label>} Mapping
                    used to redefine arbitrary labels for each of the loaded
                    channels in chanList. If there is no entry in chanLabelsMap
                    for one of the channels, or if chanLabelsMap is None, the
                    displayed channel label is the original label as obtained
                    from the recording metadata. Keys are values from chanList.
                    (default None)
                name (str | None): Name of the dataset. If specified, prepended
                    to the channel labels displayed in Sleep.

    Kwargs:
        downSample (int | float | None): Frequency in Hz at which all the data
            is subsampled. No subsampling if None (default 100.0)
        tStart (float | None): Time in seconds from start of recording of first
            loaded sample. Default 0.0
        tEnd (float | None): Time in seconds from start of recording of last
            loaded sample. Duration of recording in None. (default None)
        EMGdatapath (str or None): Path to an EMG data file created using the
            `EMGfromLFP` package (<https://github.com/csc-UW/EMGfromLFP>). If
            possible, the EMG data will be loaded, the required time segment
            extracted, resampled to match the desired sampling rate, and
            appended to the data passed to `Sleep`
        kwargs_sleep (dict): Dictionary to pass to the `Sleep` instance during
            init. (default {})
    """

    DERIVED_EMG_CHANLABEL = 'derivedEMG'

    # Mandatory and optional keys of each of the dictionaries in `datasets`
    DATASET_DICT_MANDATORY = ['binPath']
    DATASET_DICT_OPTIONAL = {
        'datatype': 'SGLX',
        'chanList': None,
        'chanLabelsMap': None,
        'name': None
    }

    ############
    # Load data from multiple datasets

    if not datasets:
        raise ValueError(f'`datasets` config entry should be a non-empty list.')

    print(f"\nLoading data from N={len(datasets)} datasets:\n")

    all_data_list = []
    all_sf = []
    chanLabels = []
    for i, dataset_dict in enumerate(datasets):

        print(f"\nLoading dataset #{i+1}/{len(datasets)} from"
              f" {dataset_dict['binPath']}")

        # Validate and set default values
        dataset_dict = validate(
            dataset_dict, mandatory=DATASET_DICT_MANDATORY,
            optional=DATASET_DICT_OPTIONAL,
            prefix='Validating `datasets` list item: '
        )

        # Preload and downsample specific parts of the data
        data, sf, chanOrigLabels = loader_switch(
            dataset_dict['binPath'],
            datatype=dataset_dict['datatype'],
            chanList=dataset_dict['chanList'],
            downSample=downSample,
            tStart=tStart,
            tEnd=tEnd,
        )

        # Relabel channels and verbose which channels are used
        labels = relabel_channels(
            chanOrigLabels,
            dataset_dict['chanLabelsMap']
        )
        # Prepend name of dataset
        if dataset_dict['name'] is not None and len(dataset_dict['name']) >= 1:
            labels = [dataset_dict['name'] + ',' + l for l in labels]
        print_used_channels(chanOrigLabels, labels)

        all_data_list.append(data)
        all_sf.append(sf)
        chanLabels += labels

    # Check consistency of data from different datasets
    # TODO: Load duration of shortest dataset if tEnd is None
    assert len(set(all_sf)) <= 1
    assert len(set([data.shape[1] for data in all_data_list])) <= 1

    data = np.concatenate(all_data_list, axis=0)

    ############
    # Load and append the EMG

    if EMGdatapath:
        print("\nLoading the EMG")
        tEnd = data.shape[1] / sf  # Will fail if EMG is shorter
        EMG_data, _ = EMGfromLFP.load_EMG(
            EMGdatapath,
            tStart=tStart,
            tEnd=tEnd,
            desired_length=data.shape[1],
        )  # Load, select time points of interest and resample

        print("Combining data and derivedEMG")
        # At this point the EMG and data should have same number of samples and
        # same sf
        data = np.concatenate((data, EMG_data), axis=0)
        chanLabels.append(DERIVED_EMG_CHANLABEL)

    ############
    # Call Sleep with loaded data

    print("\nCalling Sleep")
    Sleep(
        data=data,
        channels=chanLabels,
        sf=sf,
        **kwargs_sleep
    ).show()


def relabel_channels(chanLabels, chanLabelsMap):
    """Return remapped list of channel labels. """
    if chanLabelsMap is None:
        chanLabelsMap = {}
    missinglabels = set(chanLabelsMap.keys()) - set(chanLabels)
    if missinglabels:
        warnings.warn(
            "The following channels could not be relabelled: {missinglabels}"
        )
    relabelled_chans = [
        str(chanLabelsMap[label]) if label in chanLabelsMap else label
        for label in chanLabels
    ]
    # TODO: Fix Sleep's chanlabel "cleaning"
    return [c.replace('-', ',') for c in relabelled_chans]  # Sleep misreads '-'


def print_used_channels(chanOrigLabels, chanLabels):
    """Print which channels are used for sleepscoring."""
    print(f"Used channels:", end=' ')
    print(f"(<original label>:<displayed label> ):", end=' ')
    print(' - '.join(
        '{}:{}'.format(*tup)
        for tup in zip(chanOrigLabels, chanLabels)
    ))


def get_kwargs(func):
    """Return ``{param: default}`` dict of kwargs for function ``func``"""
    import inspect
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def get_args(func):
    """Return list of args for function ``func``."""
    import inspect
    signature = inspect.signature(func)
    return [
        k
        for k, v in signature.parameters.items()
        if v.default is inspect.Parameter.empty
    ]
