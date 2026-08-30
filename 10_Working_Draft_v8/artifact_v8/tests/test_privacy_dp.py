from __future__ import annotations

import numpy as np
import pytest

from privacy_dp_v5 import Ledger, hist


def test_histogram_user_contribution_is_bounded_by_three() -> None:
    base = [[0, 1, 2], [4, 5]]
    added_user = [0, 3, 5, 7, 11, 15]
    difference = np.abs(hist(base + [added_user]) - hist(base)).sum()
    assert difference <= 3


def test_privacy_accountant_enforces_total_budget() -> None:
    ledger = Ledger(1.0)
    for index in range(4):
        ledger.auth(f"q{index}", 0.25, 3, "person", "one count in at most three cells")
    assert ledger.spent == pytest.approx(1.0)
    with pytest.raises(ValueError, match="exhausted"):
        ledger.auth("q5", 0.25, 3, "person", "one count in at most three cells")


@pytest.mark.parametrize("epsilon,sensitivity,unit,contribution", [(0, 3, "person", "bounded"), (1, 0, "person", "bounded"), (1, 3, "", "bounded"), (1, 3, "person", "")])
def test_privacy_accountant_rejects_invalid_release_metadata(epsilon, sensitivity, unit, contribution) -> None:
    with pytest.raises(ValueError, match="invalid"):
        Ledger(4).auth("bad", epsilon, sensitivity, unit, contribution)
