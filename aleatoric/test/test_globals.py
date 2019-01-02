# Copyright 2018 Mark S. Weiss

from enum import Enum

# Very hacky, but we must put this into a separate file from test_utils so it can also be imported into
# utils.py to unit test enum_to_dict(). That function uses eval(), which in turn requires any Enum passed to it
# to be imported into the module statically. Which means this TestEnum needs to be imported. Which means we can't
# put it into test_utils where it belongs because that is a circular dependency. So it goes here and both utils
# and test_utils import it. Sorry.
# noinspection PytestWarning
ENUM_NAME = 'enum_name'
ENUM_VAL = 1


class TestEnum(Enum):
    ENUM_NAME = ENUM_VAL


