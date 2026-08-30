from __future__ import annotations

import pytest

from performance_v7 import simulate


def test_small_simulation_is_deterministic_and_finite() -> None:
    first = simulate(seed=42, rate_tps=100, duration_s=1.5)
    second = simulate(seed=42, rate_tps=100, duration_s=1.5)
    assert first["n"] > 0
    assert first["p99_ms"] == pytest.approx(second["p99_ms"])
    assert first["p50_ms"] <= first["p95_ms"] <= first["p99_ms"] <= first["max_ms"]


def test_region_loss_worsens_declared_scenario() -> None:
    normal = simulate(seed=7, rate_tps=1000, duration_s=2.0, burst=1.2, region_loss=False)
    impaired = simulate(seed=7, rate_tps=1000, duration_s=2.0, burst=1.2, region_loss=True)
    assert impaired["p99_ms"] > normal["p99_ms"]
