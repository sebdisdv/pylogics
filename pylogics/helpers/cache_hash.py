# -*- coding: utf-8 -*-
#
# This file is part of pylogics.
#
# pylogics is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pylogics is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pylogics.  If not, see <https://www.gnu.org/licenses/>.
#

"""Base classes for pylogics logic formulas."""
from abc import ABCMeta
from functools import wraps
from typing import Any, Callable, cast


def _cache_hash(fn) -> Callable[[Any], int]:
    """
    Compute the (possibly memoized) hash.

    If the hash for this object has already
    been computed, return it. Otherwise,
    compute it and store for later calls.

    :param fn: the hashing function.
    :return: the new hashing function.
    """

    @wraps(fn)
    def __hash__(self):
        if not hasattr(self, "__hash"):
            self.__hash = fn(self)
        return cast(int, self.__hash)

    return __hash__


def _getstate(fn):
    """
    Get the state.

    We need to ignore the hash value because in case the object
    is serialized with e.g. Pickle, if the state is restored
    with another instance of the interpreter, the stored hash might
    be inconsistent with the PYTHONHASHSEED initialization of the
    new interpreter.
    """

    @wraps(fn)
    def __getstate__(self):
        d = fn(self)
        d.pop("__hash")
        return d

    return __getstate__


def _setstate(fn):
    """
    Set the state.

    The hash value needs to be set to None
    as the state might be restored in another
    interpreter in which the old hash value
    might not be consistent anymore.
    """

    @wraps(fn)
    def __setstate__(self):
        fn(self)
        self.__hash = None

    return __setstate__


class Hashable(ABCMeta):
    """
    A metaclass that makes class instances to cache their hash.

    It sets:
        __hash__
        __getstate__
        __setstate__

    """

    def __new__(mcs, *args, **kwargs):
        """Create a new instance."""
        class_ = super().__new__(mcs, *args, **kwargs)

        class_.__hash__ = _cache_hash(class_.__hash__)
        class_.__getstate__ = _getstate
        class_.__setstate__ = _setstate
        return class_
