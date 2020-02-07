"""Load and sleepscore using visbrain.Sleep datasets in multiple formats."""

import os.path
import warnings
# import subprocess
from pathlib import Path

import numpy as np
import yaml

import EMGfromLFP
from visbrain.gui import Sleep

from .load import loader_switch, utils

EMGCONFIGKEYS = [
    'LFP_chanList', 'LFP_downsample', 'LFP_chanListType', 'bandpass',
    'bandstop', 'sf', 'window_size'
]


def run(config_path):

    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    print(f"Sleepscore config: \n Path={config_path}, \n Config={config}, \n")
    
    binPath = config.pop('binPath')

    load_and_score(binPath, **config)


def load_and_score(binPath, datatype='SGLX', downSample=100.0, tStart=None,
                   tEnd=None, chanList=None, chanListType='indices',
                   chanLabelsMap=None, unit='uV', EMGdatapath=None,
                   kwargs_sleep={}):
    """Load data and run visbrain's Sleep.

    Args:
        binPath (str | pathlib.Path): Path to bin of recording

    Kwargs:
        datatype (str): 'SGLX' or 'OpenEphys' (default 'SGLX')
        downSample (int | float | None): Frequency in Hz at which the data is
            subsampled. No subsampling if None, except if we load a derived-EMG.
            In this case we set the downsampling frequency to the sampling
            frequency of the EEG. (default 100.0)
        tStart (float | None): Time in seconds from start of recording of first
            loaded sample. Default 0.0
        tEnd (float | None): Time in seconds from start of recording of last
            loaded sample. Duration of recording by default
        chanList (list(int) | None): List of loaded channels. All channels are
            loaded by default. Either interpreted as channel labels or indices
            in the saved recording depending on the value of the chanListType
            parameter.
        ChanListType (str): 'indices' or 'label'. If 'indices', chanList is
            interpreted as indices of saved channels. If 'labels', chanList is
            interpreted as labels of channels (can be different since)
            (default 'indices')
        chanLabelsMap (dict | None): {<label>: <new_label>} Mapping used to
            redefine arbitrary labels for each of the loaded channels in
            chanList. If there is no entry in chanLabelsMap for one of the
            channels, or if chanLabelsMap is None,
            the displayed channel label is the original label as obtained
            from the recording metadata. Keys are channel labels. (default None)
        unit (str): 'uV' or 'mV'. Unit the data is converted into
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
    data, sf, chanOrigLabels, unit = loader_switch(
        binPath,
        datatype=datatype,
        downSample=downSample,
        tStart=tStart,
        tEnd=tEnd,
        chanList=chanList,
        chanListType=chanListType,
        unit=unit
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
    """Return remapped list of channel labels."""
    if chanLabelsMap is None:
        return chanLabels
    missinglabels = set(chanLabelsMap.keys()) - set(chanLabels)
    if missinglabels:
        warnings.warn(
            "The following channels could not be relabelled: {missinglabels}"
        )
    return [
        chanLabelsMap[label] if label in chanLabelsMap else label
        for label in chanLabels
    ]


def print_used_channels(chanOrigLabels, chanLabels):
    """Print which channels are used for sleepscoring."""
    print(f"Used channels:", end=' ')
    print(f"(<original label>:<displayed label> ):", end=' ')
    print(' - '.join(
        '{}:{}'.format(*tup)
        for tup in zip(chanOrigLabels, chanLabels)
    ))
