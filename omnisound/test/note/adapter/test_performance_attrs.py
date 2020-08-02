# Copyright 2018 Mark S. Weiss

import pytest

from omnisound.note.adapter.performance_attrs import PerformanceAttrs

ATTR_NAME = 'test_attr'
ATTR_VAL = 100
ATTR_TYPE = int


def test_performance_attrs_freeze_unfreeze():
    # Initial state is not frozen. User must explicitly freeze()
    perf_attrs = PerformanceAttrs()
    assert not perf_attrs.is_frozen()
    perf_attrs.freeze()
    assert perf_attrs.is_frozen()
    perf_attrs.unfreeze()
    assert not perf_attrs.is_frozen()


def test_performance_attrs_add_attr_set_attr():
    # Initial state is not frozen. User must explicitly freeze()
    perf_attrs = PerformanceAttrs()
    perf_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    # ATTR_NAME = 'test_attr'
    # noinspection PyUnresolvedReferences
    assert perf_attrs.test_attr == ATTR_VAL
    # noinspection PyUnresolvedReferences
    assert isinstance(perf_attrs.test_attr, ATTR_TYPE)

    new_attr_val = 200
    perf_attrs.safe_set_attr(ATTR_NAME, new_attr_val)
    # noinspection PyUnresolvedReferences
    assert perf_attrs.test_attr == new_attr_val

    with pytest.raises(ValueError):
        perf_attrs.safe_set_attr('NOT_AN_ATTR_NAME', ATTR_VAL)
    # noinspection PyUnresolvedReferences
    assert perf_attrs.test_attr == new_attr_val

    with pytest.raises(ValueError):
        perf_attrs.safe_set_attr(ATTR_NAME, float(ATTR_VAL))
    # noinspection PyUnresolvedReferences
    assert perf_attrs.test_attr == new_attr_val


def test_performance_attrs_str():
    perf_attrs = PerformanceAttrs()
    perf_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    assert f'{ATTR_NAME}: {ATTR_VAL}' == str(perf_attrs)
    perf_attrs.add_attr(ATTR_NAME + '_2', ATTR_VAL + 100, ATTR_TYPE)
    assert f'{ATTR_NAME}: {ATTR_VAL} {ATTR_NAME}_2: {ATTR_VAL + 100}' == str(perf_attrs)


def test_performance_attrs_dict():
    perf_attrs = PerformanceAttrs()
    perf_attrs.add_attr(ATTR_NAME, ATTR_VAL, ATTR_TYPE)
    assert {ATTR_NAME: ATTR_VAL} == perf_attrs.as_dict()

    new_attr_name = ATTR_NAME + '_2'
    new_attr_val = ATTR_VAL + 100
    perf_attrs.add_attr(new_attr_name, new_attr_val, ATTR_TYPE)
    assert {ATTR_NAME: ATTR_VAL, new_attr_name: new_attr_val} == perf_attrs.as_dict()


if __name__ == '__main__':
    pytest.main(['-xrf'])
