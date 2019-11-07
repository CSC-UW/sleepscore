"""Utility functions for data loading and transformation."""

import numpy as np

def get_dsf(downsample, sf):
    """Get the downsampling factor.

    Parameters
    ----------
    downsample : float
        The down-sampling frequency.
    sf : float
        The sampling frequency
    """
    if all([isinstance(k, (int, float)) for k in (downsample, sf)]):
        dsf = int(np.round(sf / downsample))
        downsample = float(sf / dsf)
        return dsf, downsample
    else:
        return 1, downsample
