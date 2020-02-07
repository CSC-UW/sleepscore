"""Load data in multiple formats as memmaps or arrays."""
from . import readSGLX as SGLX
from pathlib import Path
from . import utils


def loader_switch(binPath, *args, datatype='SGLX', **kwargs):
    """Pipe to correct function for array loading.

    Args:
        binPath (str or pathlib.Path): Path to binary data
        datatype (str): 'SGLX' or 'OpenEphys' (default 'SGLX')
        *args: Passed to loading function for the considered data format

    Kwargs:
        *kwargs: Passed to loading function for the considered data format
    """
    assert datatype in ['SGLX', 'OpenEphys'], (
        f'Data format: {datatype} not supported'
    )
    if datatype == 'SGLX':
        data, sf, channels, unit = read_SGLX(
            binPath,
            **kwargs
        )
    elif datatype == 'OpenEphys':
        raise NotImplementedError

    print_loading_output(binPath, data, sf, channels, unit)
    return data, sf, channels, unit


def print_loading_output(binPath, data, sf, channels, unit):
    info = ("Data successfully loaded (%s):"
            "\n- Down-sampling frequency : %.2fHz"
            "\n- Number of time points (after down-sampling): %i"
            "\n- Number of channels : %i"
            "\n- Unit : %s"
            )
    print(info % (binPath, sf, data.shape[1], len(channels), unit))


def read_SGLX(binPath, downSample=None, tStart=None, tEnd=None, chanList=None,
              chanListType='labels', unit='uV'):
    """Load SpikeGLX data.

    Args:
        binPath (str | pathlib.Path): Path to bin of recording

    Kwargs:
        downSample (int | float | None): Frequency in Hz at which the data is
            subsampled. No subsampling if None. (default None)
        tStart (float | None): Time in seconds from start of recording of first
            loaded sample. Default 0.0
        tEnd (float | None): Time in seconds from start of recording of last
            loaded sample. Duration of recording by default
        chanList (list(int) | None): List of loaded channels. All channels are
            loaded by default.
        ChanListType (str): 'indices' or 'label'. If 'indices', chanList is
            interpreted as indices of saved channels. If 'labels', chanList is
            interpreted as labels of channels (eg: "LF0;384")
            not all channels are saved on file during a recording. (default
            'labels')
        unit (str): 'uV' or 'mV'. Unit the data is converted into

    Returns:
        data (np.ndarray): The raw data of shape (n_channels, n_points)
        downsample (float):The down-sampling frequency used.
        channels (list(str)): List of channel names / original indices
        unit (str): Unit of returned data
    """
    print(f"Load SpikeGLX data at {binPath}")
    meta = SGLX.readMeta(Path(binPath))
    sRate = SGLX.SampRate(meta)

    # Indices in recording of first and last loaded samples
    if tStart is None:
        tStart = 0.0
    if tEnd is None:
        tEnd = float(meta['fileTimeSecs'])
    assert tStart <= tEnd
    firstSamp = int(sRate*tStart)
    lastSamp = int(sRate*tEnd)
    print(f"Will load data from tStart={tStart}s to tEnd={tEnd}s")

    # Indices of loaded channels in recording, and original labels
    savedLabels = SGLX.savedChanLabels(meta)
    chanIdxList, chanLblList = get_loaded_chans_idx_labels(
        chanList, chanListType, savedLabels
    )
    print(f"Will load N={len(chanIdxList)}/{len(savedLabels)} channels")

    # Downsampling factor
    if downSample is None:
        downSample = sRate
    assert downSample <= sRate
    dsf, downSample = utils.get_dsf(downSample, sRate)
    print(f"Will downsample from {sRate}Hz to {downSample}Hz")

    print("Loading data of interest...")
    # Load RAW data and slice out data of interest
    DataRaw = SGLX.makeMemMapRaw(binPath, meta)[
        chanIdxList,
        firstSamp:lastSamp+1:dsf
    ]

    # Convert raw data to requested unit
    # This transforms the memmap into nparray
    print(f"Convert data to {unit}")
    assert unit.lower() in ['uv', 'mv']
    if unit.lower() == 'uv':
        factor = 1.e6
    elif unit.lower() == 'mv':
        factor = 1.e3
    if meta['typeThis'] == 'imec':
        # apply gain correction and convert
        convData = factor * SGLX.GainCorrectIM(DataRaw, chanIdxList, meta)
    else:
        # apply gain correction and convert
        convData = factor * SGLX.GainCorrectNI(DataRaw, chanIdxList, meta)

    return convData, downSample, chanLblList, unit


def get_loaded_chans_idx_labels(chanList, chanListType, savedLabels):
    """Return lists of indices and labels of loaded channels."""
    if chanList is None or chanList == 'all':
        # Load all channels
        chanList = range(0, len(savedLabels))
        chanListType = 'indices'
    assert chanListType in ['indices', 'labels']
    if chanListType == 'indices':
        # Interpret the list of channels as a list of indices in saved recording
        chanIdxList = [int(c) for c in chanList]
        chanLblList = [savedLabels[i] for i in chanIdxList]
    elif chanListType == 'labels':
        errorchans = set(chanList) - set(savedLabels)
        if errorchans:
            raise Exception(
                f"The following channels labels were not found in data:"
                f"{errorchans}\n"
                f"Below are the labels of saved channels in the recording:\n"
                f"{savedLabels}"
            )
        # Interpret the list of channels as a list of labels
        chanIdxList, chanLblList = zip(
            *enumerate([l for l in savedLabels if l in chanList])
        )
    return list(chanIdxList), list(chanLblList)
