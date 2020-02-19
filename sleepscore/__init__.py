"""Load and sleepscore using visbrain.Sleep datasets in multiple formats."""

import warnings

import numpy as np
import yaml

import EMGfromLFP
from visbrain.gui import Sleep

from .load import loader_switch


def run(config_path):

    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    print(f"Sleepscore config: \n Path={config_path}, \n Config={config}, \n")

    # Validate keys in config
    df_values = get_default_args(load_and_score)
    for k, v in [(k, v) for k, v in df_values.items() if k not in config]:
        print(f"Key {k} is missing from config. Using its default value: {v}")
    for k in [k for k in config if k not in df_values]:
        print(f"Config key {k} is not recognized")
    
    binPath = config.pop('binPath')

    load_and_score(binPath, **config)


def load_and_score(binPath, datatype=None, downSample=100.0, tStart=None,
                   tEnd=None, chanList=None, chanLabelsMap=None,
                   EMGdatapath=None, kwargs_sleep={}):
    """Load data and run visbrain's Sleep.

    Args:
        binPath (str | pathlib.Path): Path to bin of recording

    Kwargs:
        datatype (str): 'SGLX' , 'TDT' or 'OpenEphys' (default 'SGLX')
        downSample (int | float | None): Frequency in Hz at which the data is
            subsampled. No subsampling if None (default 100.0)
        tStart (float | None): Time in seconds from start of recording of first
            loaded sample. Default 0.0
        tEnd (float | None): Time in seconds from start of recording of last
            loaded sample. Duration of recording in None. (default None)
        chanList (list(str) | None): List of loaded channels. All
            channels are loaded by default. (default None)
                - for SGLX data: `chanList` is interpreted
                as labels of channels,
                  eg: ["LF0;384", "LF1;385"]
                - for TDT data: Values in ChanList should be string formatted as
                follows::
                    [<score_name>-<channel_index>, ...]
                Where channels are 1-indexed, (IMPORTANT) not 0-indexed (for
                consistency with tdt methods)
                    eg: [LFPs-1, LFPs-2, EEGs-1, EEGs-94, EMGs-1...]
        chanLabelsMap (dict | None): {<channel>: <new_label>} Mapping used to
            redefine arbitrary labels for each of the loaded channels in
            chanList. If there is no entry in chanLabelsMap for one of the
            channels, or if chanLabelsMap is None,
            the displayed channel label is the original label as obtained
            from the recording metadata. Keys are values from chanList. (default
            None)
        EMGdatapath (str or None): Path to an EMG data file created using the
            `EMGfromLFP` package (<https://github.com/csc-UW/EMGfromLFP>). If
            possible, the EMG data will be loaded, the required time segment
            extracted, resampled to match the desired sampling rate, and
            appended to the data passed to `Sleep`
        kwargs_sleep (dict): Dictionary to pass to the `Sleep` instance during
            init. (default {})
    """

    # Preload and downsample specific parts of the data
    print("\nLoading data")
    data, sf, chanOrigLabels = loader_switch(
        binPath,
        datatype=datatype,
        downSample=downSample,
        tStart=tStart,
        tEnd=tEnd,
        chanList=chanList,
    )

    # Load the EMG
    if EMGdatapath:
        print("\nLoading the EMG")
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
        EMGlabel = 'derivedEMG'
        chanOrigLabels.append(EMGlabel)

    # Relabel channels and verbose which channels are used
    chanLabels = relabel_channels(chanOrigLabels, chanLabelsMap)
    print_used_channels(chanOrigLabels, chanLabels)

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
        chanLabelsMap[label] if label in chanLabelsMap else label
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


def get_default_args(func):
    import inspect
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        # if v.default is not inspect.Parameter.empty
    }
