# Repair log

Study group: 3   Members: Cruz, Maureen Joi, Lista, Patrick Raphael, Olaybar, Audrey Paulynne, Pascual, Patricia Mae Ann, Zapata, Gianela

## Defects

| # | Symptom (what was wrong for the user) | Cause (file, function, line; why it was wrong) | Fix (what you changed) | Test that now guards it | Fixed by |
| --- | --- | --- | --- | --- | --- |
<<<<<<< HEAD
| 1 | | | | | |
<<<<<<< HEAD
| 2 | Dashboard showed the strongest quake at 14:37 Manila time on 2 Dec 2023, but it happened at 22:37. | `features_stage()` in `quakewatch.py`: `tz_localize(None).tz_localize("Asia/Manila")` relabels the UTC clock time as Manila time instead of converting it, so every local time was 8 hours early. | Replaced with `t["time"].dt.tz_convert("Asia/Manila")`. | `tests/test_features.py::test_strongest_event_is_at_night_in_manila`; `tests/test_group.py::test_local_time_is_manila_not_utc` | Gianela Zapata |
=======
| 1 | `python run.py` stops with `KeyError: 'depth'` before writing the dashboard, and `features_stage()` tests error with `KeyError: 'depth'`. | `quakewatch.py`, `features_stage()`, line 184: called `depth_class(t["depth"])`, whereas the schema column created by `features_to_table()` and `integrate()` is `"depth_km"`. | Updated `t["depth_class"] = depth_class(t["depth"])` to `t["depth_class"] = depth_class(t["depth_km"])` in `features_stage()`. | `tests/test_group.py::test_group_features_stage_depth_class_uses_depth_km` | Patrick Raphael Lista |
| 2 | | | | | |
>>>>>>> origin/member1-defect1
| 3 | | | | | |
<<<<<<< HEAD
=======
| 2 | | | | | |
| 3 | A magnitude 6.0 earthquake is labelled *Moderate* instead of *Strong*. | `quakewatch.py`, `MAG_BINS` (line 33) and `mag_class()`: upper bin edge for Moderate was `6.05` instead of `5.95`, placing `6.0` inside `(4.95, 6.05]`. | Changed `MAG_BINS` from `[4.95, 6.05, 6.95, 7.95, 10]` to `[4.95, 5.95, 6.95, 7.95, 10]`. | `tests/test_features.py::<test_name_in_test_features.py>` | Maureen Joi Cruz |
>>>>>>> origin/maui-defect-3
| 4 | | | | | |
=======
| 4 | Earthquakes east of Mindanao were assigned to a nearest city in northern Luzon (>1,000 km away). | `quakewatch.py`, `nearest_city()` (line 113): `events["longitude"]` and `events["latitude"]` were passed in reversed order (`lon`, `lat`) as the first two arguments to `haversine_km(lat1, lon1, lat2, lon2)`, corrupting distance calculations. | Swapped the first two arguments in `nearest_city()` to pass `events["latitude"]` as `lat1` and `events["longitude"]` as `lon1` (and added an empty-DataFrame guard). | `tests/test_integrate.py::test_nearest_city_of_known_events` and `tests/test_group.py::test_nearest_city_does_not_swap_lat_lon` | Patricia Pascual |
>>>>>>> origin/patricia-defect-4
| 5 | Running the pipeline twice duplicates all 462 rows in `data/raw`. | `quakewatch.py`, `load_new()`, line 87: always queried from `FIRST_DAY` instead of checking `watermark()`. | Updated `load_new()` to check `watermark()` and fetch/save only events with `time > wm`. | `tests/test_acquire.py::test_second_load_adds_nothing` & `tests/test_acquire.py::test_ids_stay_unique_after_two_loads` | Audrey Olaybar |
| 6 | A test row with `depth_km = -5` enters `data/clean` with `0` rows rejected. | `quakewatch.py`, `split_by_contract()`, lines 118–124: caught `CONTRACT.validate(raw)` errors with `pass` instead of separating failing rows. | Updated `split_by_contract()` to run `CONTRACT.validate(raw, lazy=True)` and split `err.failure_cases["index"]` into `rejects`. | `tests/test_integrate.py::test_bad_rows_are_set_aside` & `tests/test_group.py::test_group_negative_depth_row_is_rejected` | Audrey Olaybar |

## Our own tests (in `tests/test_group.py`)

| Test name | Tool used (`parametrize`, fake API, `caplog`) | What it proves | Fails on the broken code? | Written by |
| --- | --- | --- | --- | --- |
| `test_group_negative_depth_row_is_rejected` | `tmp_path` & `monkeypatch` (regression test) | Proves that rows with `depth_km < 0` are excluded from `data/clean/events.parquet` and written to `data/clean/rejects.csv`. | Yes | Audrey Olaybar |
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
| `test_local_time_is_manila_not_utc` | fake API (`responses`) | A 14:37 UTC event is reported as 22:37 Manila time | Yes: gives '2023-12-02 14:37' instead of '22:37' | Gianela Zapata |
=======
| `test_integrate_logs_warning_on_rejected_rows` | `caplog` | Proves `integrate()` logs a `WARNING` message with the rejected row count whenever invalid rows fail the data contract. | Yes | Maureen Joi Cruz |
>>>>>>> origin/maui-defect-3
=======
| `test_group_features_stage_depth_class_uses_depth_km` | `@pytest.mark.parametrize`, `tmp_path` & `monkeypatch` | Proves `features_stage()` reads `"depth_km"` without raising `KeyError: 'depth'` and classifies shallow, intermediate, and deep events accurately. | Yes | Patrick Raphael Lista |
>>>>>>> origin/member1-defect1
=======
| --- | --- | --- | --- | --- |
| `test_nearest_city_does_not_swap_lat_lon` | Custom unit / regression test (`np.isclose`) | Proves `nearest_city()` uses `(latitude, longitude)` order and matches exact Haversine distances rather than transposed coordinates. | Yes | Patricia Pascual |
>>>>>>> origin/patricia-defect-4
| | | | | |

## Logging we added

| Where (function) | Level | Message | Why this level |
| --- | --- | --- | --- |
<<<<<<< HEAD
| | | | |
| `integrate()` (`quakewatch.py`) | `WARNING` | `integrate: %d row(s) rejected by contract` | Alerts operators when incoming data fails validation and is dropped from the clean dataset without halting the pipeline. |
=======
| `quakewatch.py` (`split_by_contract`) | `ERROR` (via `log.exception`) | `"integrate: schema contract failed with %d validation error(s)"` | Captures the caught `pa.errors.SchemaErrors` exception along with its full stack trace in `logs/run.log` for debugging data contract violations. |

| | | | |
>>>>>>> origin/patricia-defect-4
| | | | |

## One thing we learned about debugging

Fixing one defect at a time and immediately running `pytest` after every change made it obvious which exact line resolved each failure without masking downstream bugs. Checking failure cases explicitly—such as using Pandera's `lazy=True` validation and watermark timestamps—also taught us never to swallow exceptions silently with `pass` in a data pipeline.


