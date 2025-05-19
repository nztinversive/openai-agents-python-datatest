import pathlib

from csv_loader import load_csv


def test_load_csv_shape():
    path = pathlib.Path(__file__).parent / "fixtures" / "sample.csv"
    df = load_csv(path)
    assert len(df.rows) == 3
    assert len(df.rows[0]) == 3
