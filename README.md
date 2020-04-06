# Sleepscore

This repository allows one to perform sleepscoring of neural recording using the
`Sleep` GUI from Visbrain ( <http://visbrain.org> ) using the following steps:

-   load specific aspects of a dataset saved in multiple formats
-   (Optional) Compute or load a derived-EMG using the method from <https://github.com/buzsakilab/buzcode/blob/master/detectors/bz_EMGFromLFP.m>
-   launch the Sleep GUI, which can be used to generate a hypnogram
-   postprocess the hypnogram

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

    1.  Download the package at <https://github.com/TomBugnon/visbrain>
    1.  Install the downloaded package (make sure you're within the virtual environment)

```
# From the `visbrain` directory you just downloaded
pip install -e .
```
2.  __Install `sleepscore`___

```
# From the `sleepscore` directory you just downloaded
pip install -e .
```


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
            `EMGfromLFP` package (<https://github.com/csc-UW/EMGfromLFP>). If
            possible, the EMG data will be loaded, the required time segment
            extracted, resampled to match the desired sampling rate, and
            appended to the data passed to `Sleep`
        kwargs_sleep (dict): Dictionary to pass to the `Sleep` instance during
            init. (default {})
    """
```

1.  Run the package using either of the following:


- From the command line (make sure you're in your virtualenvironment)
  
`python -m sleepscore <path_to_config_file>`

- From python:

```python
import sleepscore

sleepscore.run(<path_to_config_file>)
```

Alternatively, `python run.py` will run the default config file.
