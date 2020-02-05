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
              chanListType='indices', unit='uV'):
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
            interpreted as original indices of channels (can be different since)
            not all channels are saved on file during a recording. (default
            'indices')
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

    def parse_snsChanMap(meta):
        """Parse channel labels / channel id info in meta['snsChanMap'].

        It is ridiculous that we have to do this ourselves.
        meta['snsChanMap'] is formatted as follows::
            (384,384,1)(AP0;0:0)(AP1;1:1)(...)...
        """
        mapstring = meta['snsChanMap']
        maptuples = mapstring.strip(')(').split(')(')[1:]
        snsChanMap_parsed = [
            chaninfo.split(sep=':')
            for chaninfo in maptuples
        ]  # List of tuples: [(<chan_name>, <chan_orig_index>),...]
        assert all(
            [len(tup) == 2 for tup in snsChanMap_parsed]
        )  # Fails if there's ':' in the channel labels
        return snsChanMap_parsed

    # Indices of loaded channels in recording, and original labels
    nSavedChans = int(meta['nSavedChans'])
    snsChanMap = parse_snsChanMap(meta)
    if chanList is None or chanList == 'all':
        # Load all channels
        chanList = range(0, nSavedChans)
        chanListType = 'indices'
    assert chanListType in ['indices', 'labels']
    if chanListType == 'indices':
        # Interpret the list of channels as a list of indices in saved recording
        chanIdxList = [int(c) for c in chanList]
        # Get the label of each channel
        chanOrigIdxList = [
            str(c) for c in SGLX.OriginalChans(meta)[chanIdxList]
        ]  # Original channel Ids (amongst all channels,not only the ones saved)
        #
        labelmap = dict([(orig_i, label) for label, orig_i in snsChanMap])
        chanLblList = [labelmap[orig_i] for orig_i in chanOrigIdxList]
    elif chanListType == 'labels':
        # Interpret the list of channels as a list of labels (indices on the
        # probe)
        raise NotImplementedError
    print(f"Will load N={len(chanList)}/{nSavedChans} channels")

    # Downsampling factor
    if downSample is None:
        downSample = sRate
    assert downSample <= sRate
    dsf, downSample = utils.get_dsf(downSample, sRate)
    print(f"Will downsample from {sRate}Hz to {downSample}Hz")

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
