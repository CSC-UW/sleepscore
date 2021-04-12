# Sleepscore

This repository allows one to perform sleepscoring of neural recording using the
`Sleep` GUI from Visbrain ( <http://visbrain.org> ) using the following steps:

-   load specific aspects of one or multiple datasets saved in multiple formats
-   (Optional) Load a [derived-EMG](https://github.com/CSC-UW/emg_from_lfp).
-   launch the Sleep GUI, which can be used to generate a hypnogram
-   postprocess the hypnogram

To follow the modifications of Visbrain to facilitate scoring of animal data,
check out this issue: ``https://github.com/EtienneCmb/visbrain/issues/35``

### Installation

1.  __Create and activate a virtual environment__:

    -   On windows:

        ```
        conda create -n sleepscoring python=3.7
        conda activate sleepscoring
        ```

    -   On Mac/linux s(install `venv` (`pip install virtualenv`) and `virtualenvwrapper` (`pip install virtualenvwrapper`) first):

        ```
        mkvirtualenv --python `which python3` sleepscoring
        workon sleepscoring
        ```

1.  __Install `visbrain`__:

<!-- The changes to visbrain's Sleep module that allow sleepscoring of animal data -->
<!-- (short scoring window) have not yet been released into a new version -->
<!-- (04/19/2020), so you need to manually download and install the master branch of -->
<!-- visbrain to use those features (commit more recent than b599038): -->

<!--   1. Download or clone the master branch at https://github.com/EtienneCmb/visbrain/ -->
<!--   2. From the `visbrain` directory you just downloaded: ``pip install .`` or -->
<!--   ``pip install -e .`` -->

  1. Download https://github.com/TomBugnon/visbrain/
  2. From the `visbrain` directory you just downloaded: ``pip install -U .``

2.  __Install `sleepscore`___

Download or clone this repository. From the `sleepscore` directory you just
downloaded: `pip install .`

If you want to load TDT data there is an extra requirement:
`pip install ".[tdt]"`

3. __Install `emg_from_lfp`__:

    1. Download https://github.com/CSC-UW/emg_from_lfp
    2. From the `emg_from_lfp` directory you just downloaded: ``pip install .``

Add an `-e` option after `pip install` for editable installation.


### Usage

1.  Copy the default configuration file (`sleepscore_config_df`)

2.  Manually set the parameters for the copied config file. The meaning of each
parameter is described in the `sleepscore.load_and_score` function:

```python
    """
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
            `emg_from_lfp` package (<https://github.com/csc-UW/emg_from_lfp>). If
            possible, the EMG data will be loaded, the required time segment
            extracted, resampled to match the desired sampling rate, and
            appended to the data passed to `Sleep`
        kwargs_sleep (dict): Dictionary to pass to the `Sleep` instance during
            init. (default {})
    """
```

3.  Run the package using either of the following:


- From the command line (make sure you're in your virtualenvironment)

`python -m sleepscore <path_to_config_file>`

- From python:

```python
import sleepscore

sleepscore.run(<path_to_config_file>)
```

Alternatively, `python run.py` will run the default config file.

### Using video functionality in visbrain on Windows 10
In order to use visbrain's video functionality on Windows 10, you will need DirectShow and other Windows Media Player libraries which may or may not have already been bundled with the OS, as well as the proper codecs that DirectShow can use to display your video format of choice. For example, in order to get mp4 video functionality working on Windows 10 Education N (N = does not ship with many Microsoft multimedia features), install the Media Feature Pack and Windows Media Player OS features by following the instructions for your OS [here](https://support.microsoft.com/en-us/topic/media-feature-pack-list-for-windows-n-editions-c1c6fffa-d052-8338-7a79-a4bb980a700a). Then, get the mp4 codecs [here](https://codecguide.com/download_kl.htm). 
