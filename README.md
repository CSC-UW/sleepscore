# Sleepscore

This repository allows one to perform sleepscoring of neural recording using the
`Sleep` GUI from Visbrain ( <http://visbrain.org> ) using the following steps:

-   load specific aspects of a dataset saved in multiple formats
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


      ```
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
      ```


1.  Run the package using the following command:
  
`python sleepscore <path_to_config_file>`


Alternatively, `python run.py` will run the default config file.
