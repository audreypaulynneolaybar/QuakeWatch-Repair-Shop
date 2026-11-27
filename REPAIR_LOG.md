# Repair log

Study group: 3   Members: Cruz, Maureen Joi, Lista, Patrick Raphael, Olaybar, Audrey Paulynne, Pascual, Patricia Mae Ann, Zapata, Gianela

## Defects

| # | Symptom (what was wrong for the user) | Cause (file, function, line; why it was wrong) | Fix (what you changed) | Test that now guards it | Fixed by |
| --- | --- | --- | --- | --- | --- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | Earthquakes east of Mindanao were assigned to a nearest city in northern Luzon (>1,000 km away). | `quakewatch.py`, `nearest_city()` (line 113): `events["longitude"]` and `events["latitude"]` were passed in reversed order (`lon`, `lat`) as the first two arguments to `haversine_km(lat1, lon1, lat2, lon2)`, corrupting distance calculations. | Swapped the first two arguments in `nearest_city()` to pass `events["latitude"]` as `lat1` and `events["longitude"]` as `lon1` (and added an empty-DataFrame guard). | `tests/test_integrate.py::test_nearest_city_of_known_events` and `tests/test_group.py::test_nearest_city_does_not_swap_lat_lon` | Patricia Pascual |
| 5 | Running the pipeline twice duplicates all 462 rows in `data/raw`. | `quakewatch.py`, `load_new()`, line 87: always queried from `FIRST_DAY` instead of checking `watermark()`. | Updated `load_new()` to check `watermark()` and fetch/save only events with `time > wm`. | `tests/test_acquire.py::test_second_load_adds_nothing` & `tests/test_acquire.py::test_ids_stay_unique_after_two_loads` | Audrey Olaybar |
| 6 | A test row with `depth_km = -5` enters `data/clean` with `0` rows rejected. | `quakewatch.py`, `split_by_contract()`, lines 118–124: caught `CONTRACT.validate(raw)` errors with `pass` instead of separating failing rows. | Updated `split_by_contract()` to run `CONTRACT.validate(raw, lazy=True)` and split `err.failure_cases["index"]` into `rejects`. | `tests/test_integrate.py::test_bad_rows_are_set_aside` & `tests/test_group.py::test_group_negative_depth_row_is_rejected` | Audrey Olaybar |

## Our own tests (in `tests/test_group.py`)

| Test name | Tool used (`parametrize`, fake API, `caplog`) | What it proves | Fails on the broken code? | Written by |
| --- | --- | --- | --- | --- |
| `test_group_negative_depth_row_is_rejected` | `tmp_path` & `monkeypatch` (regression test) | Proves that rows with `depth_km < 0` are excluded from `data/clean/events.parquet` and written to `data/clean/rejects.csv`. | Yes | Audrey Olaybar |
| --- | --- | --- | --- | --- |
| `test_nearest_city_does_not_swap_lat_lon` | Custom unit / regression test (`np.isclose`) | Proves `nearest_city()` uses `(latitude, longitude)` order and matches exact Haversine distances rather than transposed coordinates. | Yes | Patricia Pascual |
| | | | | |

## Logging we added

| Where (function) | Level | Message | Why this level |
| --- | --- | --- | --- |
| `quakewatch.py` (`split_by_contract`) | `ERROR` (via `log.exception`) | `"integrate: schema contract failed with %d validation error(s)"` | Captures the caught `pa.errors.SchemaErrors` exception along with its full stack trace in `logs/run.log` for debugging data contract violations. |

| | | | |
| | | | |

## One thing we learned about debugging

Fixing one defect at a time and immediately running `pytest` after every change made it obvious which exact line resolved each failure without masking downstream bugs. Checking failure cases explicitly—such as using Pandera's `lazy=True` validation and watermark timestamps—also taught us never to swallow exceptions silently with `pass` in a data pipeline.