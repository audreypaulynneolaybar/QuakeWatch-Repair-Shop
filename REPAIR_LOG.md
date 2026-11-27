# Repair log

Study group: 3   Members: Cruz, Maureen Joi, Lista, Patrick Raphael, Olaybar, Audrey Paulynne, Pascual, Patricia Mae Ann, Zapata, Gianela

## Defects

| # | Symptom (what was wrong for the user) | Cause (file, function, line; why it was wrong) | Fix (what you changed) | Test that now guards it | Fixed by |
| --- | --- | --- | --- | --- | --- |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | Running the pipeline twice duplicates all 462 rows in `data/raw`. | `quakewatch.py`, `load_new()`, line 87: always queried from `FIRST_DAY` instead of checking `watermark()`. | Updated `load_new()` to check `watermark()` and fetch/save only events with `time > wm`. | `tests/test_acquire.py::test_second_load_adds_nothing` & `tests/test_acquire.py::test_ids_stay_unique_after_two_loads` | Audrey Olaybar |
| 6 | A test row with `depth_km = -5` enters `data/clean` with `0` rows rejected. | `quakewatch.py`, `split_by_contract()`, lines 118–124: caught `CONTRACT.validate(raw)` errors with `pass` instead of separating failing rows. | Updated `split_by_contract()` to run `CONTRACT.validate(raw, lazy=True)` and split `err.failure_cases["index"]` into `rejects`. | `tests/test_integrate.py::test_bad_rows_are_set_aside` & `tests/test_group.py::test_group_negative_depth_row_is_rejected` | Audrey Olaybar |

## Our own tests (in `tests/test_group.py`)

| Test name | Tool used (`parametrize`, fake API, `caplog`) | What it proves | Fails on the broken code? | Written by |
| --- | --- | --- | --- | --- |
| `test_group_negative_depth_row_is_rejected` | `tmp_path` & `monkeypatch` (regression test) | Proves that rows with `depth_km < 0` are excluded from `data/clean/events.parquet` and written to `data/clean/rejects.csv`. | Yes | Audrey Olaybar |
| | | | | |
| | | | | |

## Logging we added

| Where (function) | Level | Message | Why this level |
| --- | --- | --- | --- |
| | | | |
| | | | |
| | | | |

## One thing we learned about debugging

Fixing one defect at a time and immediately running `pytest` after every change made it obvious which exact line resolved each failure without masking downstream bugs. Checking failure cases explicitly—such as using Pandera's `lazy=True` validation and watermark timestamps—also taught us never to swallow exceptions silently with `pass` in a data pipeline.