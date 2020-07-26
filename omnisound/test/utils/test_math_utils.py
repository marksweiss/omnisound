# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.utils.math_utils import *


def test_sign():
    for _ in range(10):
        assert sign() in {1, -1}


if __name__ == '__main__':
    pytest.main(['-xrf'])
