#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# utils/validation.py

"""Validation and update of parameters dictionaries."""

import copy as cp


class ParameterError(ValueError):
    """Raised when there is an error with parameters"""
    pass


class ReservedParameterError(ParameterError):
    """Raised when parameter dictionary contains a reserved parameter."""
    pass


class MissingParameterError(ParameterError):
    """Raised when a mandatory parameter is missing."""
    pass


class UnrecognizedParameterError(ParameterError):
    """Raised when a parameter is not recognized."""
    pass


class MissingChildNodeError(ValueError):
    """Raised when a child `Params` node is missing."""
    pass


class UnrecognizedChildNodeError(ValueError):
    """Raised when a child `Params` node is not recognized."""
    pass


def validate(params, mandatory=None, optional=None, prefix=None):
    """Validate and set default values for parameter dictionary.

    Args:
        params (dict-like): Parameter dictionary to validate.

    Kwargs:
        mandatory (list(str) | None): List of parameters that are
            expected in the dictionary. Ignored if ``None``.
        optional (dict | None): Dict of parameters that are
            recognized but optional, along with their default value. Ignored if
            ``None``. If not None, the list of recognized parameters is
            ``mandatory + optional`` and we throw an error if one
            of the params is not recognized. Optional parameters missing from
            `params` are added along with their default value.
        prefix (str | None): If specified, prepended to error messages.
    Returns:
        params: The parameter dictionary updated with default values.
    """

    prefix = '' if prefix is None else prefix

    error_msg_base = (
        f"{prefix}Invalid parameters in dictionary: \n`{params}`.\n"
    )

    # Check that mandatory params are here
    if (
        mandatory is not None
        and any([key for key in mandatory if key not in params.keys()])
    ):
        raise MissingParameterError(
            error_msg_base + (
                f"The following parameters are mandatory: {mandatory}"
            )
        )

    # Check recognized parameters
    if optional is not None:
        assert mandatory is not None
        recognized_params = list(optional.keys()) + mandatory
        if any([key not in recognized_params for key in params.keys()]):
            raise UnrecognizedParameterError(
                error_msg_base + (
                    f"The following parameters are recognized:\n"
                    f"{mandatory} (mandatory)\n"
                    f"{list(optional.keys())} (optional)"
                )
            )

    # Add default values:
    missing_optional = {
        k: v
        for k, v in optional.items()
        if k not in params.keys()
    }
    if any(missing_optional):
        print(f"{prefix}Set default value for optional parameters:"
              f"{missing_optional}")
        params = cp.deepcopy(params)
        params.update(missing_optional)

    return params
