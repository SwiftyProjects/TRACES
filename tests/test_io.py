import numpy as np
import pandas as pd
import pytest

from traces_ts import from_frame, generate_pairs, load_data


def test_load_sample(sample_path):
    data = load_data(sample_path)
    assert data.time_column == "Time"
    assert data.series == [f"Label_{i}" for i in range(1, 11)]
    assert data.n_observations == 52
    assert data.frame.index.name == "Time"


def test_load_csv_and_named_time_column(tmp_path):
    df = pd.DataFrame(
        {"a": [1.0, 2, 3, 5], "Date": pd.date_range("2024-01-01", periods=4), "b": [2.0, 1, 4, 3]}
    )
    path = tmp_path / "data.csv"
    df.to_csv(path, index=False)
    data = load_data(path, time_column="Date")
    assert isinstance(data.frame.index, pd.DatetimeIndex)
    assert data.series == ["a", "b"]


def test_first_column_is_time_regardless_of_name():
    df = pd.DataFrame({"Week": [1, 2, 3, 4], "a": [1.0, 2, 3, 4], "b": [4.0, 3, 1, 2]})
    assert from_frame(df).time_column == "Week"


def test_datetime_index_frame_used_as_time():
    idx = pd.date_range("2024-01-01", periods=5, name="when")
    df = pd.DataFrame({"a": [1.0, 2, 3, 4, 6], "b": [2.0, 1, 4, 3, 5]}, index=idx)
    data = from_frame(df)
    assert data.time_column == "when" and data.series == ["a", "b"]


def test_unsupported_extension(tmp_path):
    path = tmp_path / "data.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="Unsupported"):
        load_data(path)


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_data(tmp_path / "nope.xlsx")


def test_non_numeric_series_rejected():
    df = pd.DataFrame({"t": [1, 2, 3], "a": ["x", "y", "z"], "b": [1.0, 2, 3]})
    with pytest.raises(ValueError, match="non-numeric"):
        from_frame(df)


def test_missing_values_policies():
    df = pd.DataFrame(
        {"t": range(6), "a": [1.0, np.nan, 3, 4, 5, 6], "b": [1.0, 2, 3, 4, 5, np.nan]}
    )
    with pytest.raises(ValueError, match="missing values"):
        from_frame(df)
    with pytest.warns(UserWarning, match="Dropped 2 rows"):
        assert len(from_frame(df, missing="drop").frame) == 4
    with pytest.warns(UserWarning, match="Interpolated"):
        out = from_frame(df, missing="interpolate").frame
    assert len(out) == 5
    assert out.loc[1, "a"] == pytest.approx(2.0)


def test_unsorted_time_is_sorted_with_warning():
    df = pd.DataFrame({"t": [3, 1, 2, 4], "a": [3.0, 1, 2, 4], "b": [1.0, 2, 3, 4]})
    with pytest.warns(UserWarning, match="sorted"):
        data = from_frame(df)
    assert list(data.frame.index) == [1, 2, 3, 4]


def test_duplicate_time_rejected():
    df = pd.DataFrame({"t": [1, 1, 2], "a": [1.0, 2, 3], "b": [1.0, 2, 3]})
    with pytest.raises(ValueError, match="duplicate"):
        from_frame(df)


def test_too_few_series_or_rows():
    with pytest.raises(ValueError, match="two series"):
        from_frame(pd.DataFrame({"t": [1, 2, 3], "a": [1.0, 2, 3]}))
    with pytest.raises(ValueError, match="observations"):
        from_frame(pd.DataFrame({"t": [1, 2], "a": [1.0, 2], "b": [2.0, 1]}))


def test_generate_pairs_with_parent_child_mapping():
    pairs = generate_pairs(["total", "a", "b", "c"], {"total": ["a", "b"]})
    assert ("total", "a") not in pairs
    assert ("total", "b") not in pairs
    assert ("total", "c") in pairs
    assert ("a", "b") in pairs
    assert len(pairs) == 4


def test_generate_pairs_with_pair_list_and_unknown_warning():
    assert generate_pairs(["a", "b", "c"], [("b", "a")]) == [("a", "c"), ("b", "c")]
    with pytest.warns(UserWarning, match="unknown"):
        generate_pairs(["a", "b"], [("a", "zzz")])
