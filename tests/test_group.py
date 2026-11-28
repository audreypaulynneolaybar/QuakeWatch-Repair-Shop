import pandas as pd
import pytest
import quakewatch as qw


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