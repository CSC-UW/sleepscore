"""Load and sleepscore using visbrain.Sleep datasets in multiple formats."""

import os.path
# import subprocess
from pathlib import Path

import numpy as np

from visbrain.gui import Sleep

from .tools import EMGfromLFP
from .load import loader_switch, utils

EMGCONFIGKEYS = [
    'LFP_chanList', 'LFP_downsample', 'LFP_chanListType', 'bandpass',
    'bandstop', 'sf', 'window_size'
]


def load_and_score(binPath, datatype='SGLX', downSample=100.0, tStart=None,
                   tEnd=None, chanList=None, chanListType='indices',
                   chanLabelsMap=None, unit='uV', add_EMG=False, save_EMG=True,
                   recompute_EMG=False, EMG_config=None, kwargs_sleep={}):
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
            loaded by default.
        ChanListType (str): 'indices' or 'label'. If 'indices', chanList is
            interpreted as indices of saved channels. If 'labels', chanList is
            interpreted as original indices of channels (can be different since)
            not all channels are saved on file during a recording. (default
            'indices')
        chanLabelsMap (dict | None): Mapping used to redefine arbitrary labels
            for each of the channels in chanList. If there is no entry in
            chanLabelsMap for one of the channels, or if chanLabelsMap is None,
            the displayed channel label is the original index/label as obtained
            from the recording metadata. (default None)
        unit (str): 'uV' or 'mV'. Unit the data is converted into
        add_EMG (bool): Do we gather and add to the data the lfp-derived EMG
            (default False)
        save_EMG (bool): Do we save newly computed EMG (default True)
        recompute_EMG (bool): Do we force recomputing of EMG.
        EMG_config (dict): TODO
        kwargs_sleep (dict): Dictionary to pass to the `Sleep` instance during
            init. (default {})
    """

    # Load or compute the EMG and select time segment of interest
    if add_EMG:
        print("\nGathering EMG")
        print(f"EMG_config={EMG_config}")
        # Make sure the derived EMG is at the same sampling frequency as the
        # data:
        if downSample is None:
            print("`downSample` is None but we load an EMG: set `downSample` to"
                  f"the EMG sf: {EMG_config['sf']}")
            downSample = EMG_config['sf']
        elif downSample != EMG_config['sf']:
            print("`downSample` != EMG_config['sf'] !"
                  f" -> Modifying `EMG_config['sf']` to {downSample}Hz")
            EMG_config['sf'] = downSample
        # Load the EMG
        EMG_data, EMG_metadata = get_EMG(
            binPath, EMG_config, datatype=datatype, save_EMG=save_EMG,
            recompute_EMG=recompute_EMG
        )
        assert EMG_metadata['sf'] == downSample
        # Select time segment of interest for EMG
        if tStart is None:
            tStart = 0.0
        firstSamp = int(tStart * EMG_metadata['sf'])
        if tEnd is None:
            lastSamp = EMG_data.shape[1]
        else:
            lastSamp = int(tEnd * EMG_metadata['sf'])
        EMG_data = EMG_data[:, firstSamp:lastSamp+1]
    else:
        print("\nIgnoring derivedEMG stuff")

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

    # Relabel channels and verbose which channels are used
    if chanList is None or chanList == 'all':
        chanList = range(len(chanOrigLabels))
    chanLabels = [
        (
            chanLabelsMap[c] if chanLabelsMap is not None and c in chanLabelsMap
            else chanOrigLabels[i]
        )
        for i, c in enumerate(chanList)
    ]
    print_used_channels(chanList, chanOrigLabels, chanLabels)

    # Combine the EMG with the data
    if add_EMG:
        print("\nCombining data and derivedEMG")
        # At this point the EMG and data should have same number of samples and
        # same sf
        data = np.concatenate((data, EMG_data), axis=0)
        chanLabels.append('derivedEMG')

    print("\nCalling Sleep")
    Sleep(
        data=data,
        channels=chanLabels,
        sf=sf,
        **kwargs_sleep
    ).show()


def print_used_channels(chanList, chanOrigLabels, chanLabels):
    """Print which channels are used for sleepscoring."""
    print(f"Used channels (<index in chanList>:<original label from file>:"
          f"<displayed label> ):", end='\n  ')
    print(' - '.join(
        '{}:{}:{}'.format(*tup)
        for tup in zip(chanList, chanOrigLabels, chanLabels)
    ))


def get_EMG(binPath, EMG_config, datatype='SGLX', save_EMG=True,
            recompute_EMG=False):
    """Load or compute the lfp-derived EMG.

    Args:
        binPath: Path to bin of recording of interest. The EMG data and metadata
            are is saved or loaded from the same directory as the raw recording

    """

    # Validate params
    assert set(EMG_config.keys()) == set(EMGCONFIGKEYS)

    # Get paths
    binPath = Path(binPath)
    EMGdatapath = Path(binPath.parent / (binPath.stem + ".derivedEMGdata.npy"))
    EMGmetapath = Path(
        binPath.parent / (binPath.stem + ".derivedEMGmetadata.yml")
    )

    # Do we compute the EMG?
    if recompute_EMG:
        print("Forcing recomputation of EMG.")
        compute_EMG = True
    # Don't recompute if it was already computed and saved with the same
    # parameters
    elif os.path.exists(EMGdatapath) and os.path.exists(EMGmetapath):
        print("Found preexisting EMG files...", end="")
        EMG_metadata = utils.load_yaml(EMGmetapath)
        if (
            not all([
                EMG_metadata[key] == value for key, value in EMG_config.items()
            ])
            or str(binPath) != EMG_metadata['binPath']
        ):
            print("...but with different parameters. Recomputing!")
            compute_EMG = True
        else:
            compute_EMG = False
    # Otherwise we compute it
    else:
        compute_EMG = True

    # Load or compute EMG
    if not compute_EMG:
        print(f"\nLoading EMG files at {EMGdatapath}, {EMGmetapath}")
        EMG_data = np.load(EMGdatapath)
        EMG_metadata = utils.load_yaml(EMGmetapath)
    else:
        print(f"Computing EMG from LFP:")
        print("Loading LFP for EMG computing")
        # Load LFP for channels of interest
        lfp, sf, chanLabels, _ = loader_switch(
            binPath,
            datatype=datatype,
            chanList=EMG_config['LFP_chanList'],
            chanListType=EMG_config['LFP_chanListType'],
            downSample=EMG_config['LFP_downsample'],
            tStart=None,
            tEnd=None,
        )
        print(f"Using the following channels for EMG derivation (labels): "
              f"{' - '.join(chanLabels)}")
        print("Computing EMG from LFP")
        EMG_data = EMGfromLFP.compute_EMG(
            lfp, sf,
            EMG_config['sf'], EMG_config['window_size'], EMG_config['bandpass'],
            EMG_config['bandstop']
        )
        # Generate EMG metadata
        EMG_metadata = EMG_config.copy()
        EMG_metadata['binPath'] = str(binPath)
        EMG_metadata['datatype'] = datatype
        EMG_metadata['EMGdatapath'] = str(EMGdatapath)
        EMG_metadata['EMGmetapath'] = str(EMGmetapath)
        EMG_metadata['LFP_chanLabels'] = chanLabels
        # EMG_metadata['gitcommit'] = subprocess.check_output(
        #     ["git", "describe"]
        # ).strip()

    # Save EMG
    if compute_EMG and save_EMG:
        print(f"Saving EMG metadata at {EMGmetapath}")
        utils.save_yaml(EMGmetapath, EMG_metadata)
        print(f"Saving EMG data at {EMGdatapath}")
        np.save(EMGdatapath, EMG_data)

    return EMG_data, EMG_metadata
