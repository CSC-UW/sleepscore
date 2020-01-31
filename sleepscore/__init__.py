"""Load and sleepscore using visbrain.Sleep datasets in multiple formats."""

from visbrain.gui import Sleep

from .load import loader_switch

def load_and_score(binPath, datatype='SGLX', downSample=100.0, tStart=None,
                   tEnd=None, chanList=None, chanListType='indices',
                   chanLabelsMap=None, unit='uV', kwargs_sleep={}):
    """Load data and run visbrain's Sleep.
    
    Args:
        binPath (str | pathlib.Path): Path to bin of recording
    
    Kwargs:
        datatype (str): 'SGLX' or 'OpenEphys' (default 'SGLX')
        downSample (int | float | None): Frequency in Hz at which the data is
            subsampled. No subsampling if None. (default 100.0)
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
        kwargs_sleep (dict): Dictionary to pass to the `Sleep` instance during
            init. (default {})
    """
    # Preload and downsample specific parts of the data
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
    chanLabels = [
        (
            chanLabelsMap[c] if chanLabelsMap is not None and c in chanLabelsMap
            else chanOrigLabels[i]
        )
        for i, c in enumerate(chanList)
    ]
    print_used_channels(chanList, chanOrigLabels, chanLabels)

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
