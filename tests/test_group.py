from datetime import datetime, timezone

import pandas as pd
import quakewatch as qw
import responses


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