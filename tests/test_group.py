<<<<<<< HEAD
from datetime import datetime, timezone

=======
import logging
>>>>>>> origin/maui-defect-3
import pandas as pd
import pytest
import quakewatch as qw
<<<<<<< HEAD
import responses
=======
import numpy as np
>>>>>>> origin/patricia-defect-4


def test_group_negative_depth_row_is_rejected(tmp_path, monkeypatch):
    """Defect #6 regression test: rows with depth_km < 0 must not enter data/clean."""
    raw_dir = tmp_path / "raw" / "year=2023"
    raw_dir.mkdir(parents=True)
    clean_dir = tmp_path / "clean"
    monkeypatch.setattr(qw, "RAW", tmp_path / "raw")
    monkeypatch.setattr(qw, "CLEAN", clean_dir)

    df = pd.DataFrame([
        {
            "id": "valid-eq-1",
            "time": pd.Timestamp("2023-12-02T14:37:00Z"),
            "latitude": 8.5,
            "longitude": 126.4,
            "depth_km": 12.0,
            "mag": 6.1,
            "magType": "mww",
            "place": "Mindanao",
        },
        {
            "id": "invalid-neg-depth",
            "time": pd.Timestamp("2023-12-03T10:00:00Z"),
            "latitude": 8.6,
            "longitude": 126.5,
            "depth_km": -5.0,
            "mag": 5.5,
            "magType": "mb",
            "place": "Mindanao",
        },
    ])
    df.to_parquet(raw_dir / "events_test.parquet", index=False)

    qw.integrate()

    clean_df = pd.read_parquet(clean_dir / "events.parquet")
    rejects_df = pd.read_csv(clean_dir / "rejects.csv")

    assert "valid-eq-1" in set(clean_df["id"])
    assert "invalid-neg-depth" not in set(clean_df["id"])
    assert "invalid-neg-depth" in set(rejects_df["id"])

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
def _fake_feature():
    t = datetime(2023, 12, 2, 14, 37, tzinfo=timezone.utc)
    return {
        "type": "Feature",
        "id": "fake000001",
        "properties": {"mag": 7.6, "place": "Fake place", "magType": "mww",
                       "time": int(t.timestamp() * 1000)},
        "geometry": {"type": "Point", "coordinates": [126.0, 8.5, 30.0]},
    }


@responses.activate
def test_local_time_is_manila_not_utc(project):
    responses.add(
        responses.GET,
        f"{qw.BASE}/fdsnws/event/1/query",
        json={"type": "FeatureCollection", "features": [_fake_feature()]},
        status=200,
    )

    assert qw.load_new() == 1
    qw.integrate()
    feat = qw.features_stage()

    row = feat.iloc[0]
    assert row["local"].strftime("%Y-%m-%d %H:%M") == "2023-12-02 22:37"
    assert row["hour_local"] == 22
=======

def test_integrate_logs_warning_on_rejected_rows(loaded, caplog):
    """Verify integrate() emits a WARNING log when contract-violating rows are rejected."""
    bad_row = pd.DataFrame([{
        "id": "bad_depth_test_1",
        "time": pd.Timestamp("2023-06-01T00:00:00Z"),
        "latitude": 14.5,
        "longitude": 121.0,
        "depth_km": -5.0,  # violates depth_km between(0, 700)
        "mag": 5.5,
        "magType": "mww",
        "place": "Test invalid depth event",
    }])
    qw.save_raw(bad_row)

    with caplog.at_level(logging.WARNING, logger="quakewatch"):
        qw.integrate()

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) >= 1, "Expected a WARNING log when rows are rejected"
    assert "1" in warnings[0].getMessage() and "reject" in warnings[0].getMessage().lower()
>>>>>>> origin/maui-defect-3
=======

@pytest.mark.parametrize(
    "depth_km, expected_class",
    [
        (10.0, "shallow"),
        (100.0, "intermediate"),
        (400.0, "deep"),
    ],
)
def test_group_features_stage_depth_class_uses_depth_km(
    tmp_path, monkeypatch, depth_km, expected_class
):
    """Defect #1 regression test: features_stage must read depth_km without KeyError: 'depth'."""
    clean_dir = tmp_path / "clean"
    feat_dir = tmp_path / "features"
    clean_dir.mkdir(parents=True)
    feat_dir.mkdir(parents=True)

    monkeypatch.setattr(qw, "CLEAN", clean_dir)
    monkeypatch.setattr(qw, "FEAT", feat_dir)

    clean_df = pd.DataFrame([
        {
            "id": "eq-depth-test",
            "time": pd.Timestamp("2023-12-02T14:37:00Z"),
            "latitude": 8.5,
            "longitude": 126.4,
            "depth_km": depth_km,
            "mag": 6.5,
            "magType": "mww",
            "place": "Mindanao",
            "city_id": "C10",
            "city_name": "Davao",
            "dist_km": 50.0,
        }
    ])
    clean_df.to_parquet(clean_dir / "events.parquet", index=False)

    feat_df = qw.features_stage()
    assert feat_df["depth_class"].iloc[0] == expected_class
>>>>>>> origin/member1-defect1
=======
def test_nearest_city_does_not_swap_lat_lon():
    """Defect #4 regression test: nearest_city must use (lat, lon) rather than swapped (lon, lat)."""
    cities = pd.DataFrame({
        "city_id": ["C_NEAR", "C_FAR"],
        "lgu_name": ["Near City", "Far City"],
        "latitude": [7.0, 17.5],
        "longitude": [126.1, 121.5],
    })
    events = pd.DataFrame({
        "latitude": [7.0],
        "longitude": [126.0],
    })

    city_ids, distances = qw.nearest_city(events, cities)

    assert city_ids[0] == "C_NEAR"
    assert np.isclose(distances[0], qw.haversine_km(7.0, 126.0, 7.0, 126.1), atol=1e-6)
>>>>>>> origin/patricia-defect-4
