"""Load and sleepscore using visbrain.Sleep datasets in multiple formats."""

from visbrain.gui import Sleep
from pathlib import Path
from tkinter import Tk
from tkinter import filedialog

from .load import loader_switch

def load_and_score(binPath, datatype='SGLX', downSample=100.0, tStart=None,
                   tEnd=None, chanList=None, chanListType='indices', unit='uV',
                   kwargs_sleep={}):
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
        unit (str): 'uV' or 'mV'. Unit the data is converted into
        kwargs_sleep (dict): Dictionary to pass to the `Sleep` instance during
            init. (default {})
    """
    data, sf, channels, unit = loader_switch(
        binPath,
        datatype=datatype,
        downSample=downSample,
        tStart=tStart,
        tEnd=tEnd,
        chanList=chanList,
        chanListType=chanListType,
        unit=unit
    )

    Sleep(
        data=data, 
        channels=channels,
        sf=sf,
        **kwargs_sleep
    ).show()
