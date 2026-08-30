from __future__ import annotations

import numpy as np

from sanctions_v6 import ownership_engine
from sanctions_v7 import own_engine, ownership_properties


def test_direct_and_indirect_fifty_percent_rule() -> None:
    edges = [(0, 2, 0.25), (1, 2, 0.25), (2, 3, 0.50)]
    status = ownership_engine(edges, {0, 1})
    assert status[2]
    assert status[3]


def test_below_threshold_does_not_propagate() -> None:
    edges = [(0, 1, 0.49), (1, 2, 0.90)]
    status = own_engine(edges, {0}, 3)
    assert status.tolist() == [True, False, False]


def test_monotonicity_property_suite_is_reproducible() -> None:
    passed, total = ownership_properties(np.random.default_rng(20260807), n=500)
    assert total == 500
    assert passed == 500
