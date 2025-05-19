from csv_mcp.csv_loader import load_csv, preview_df


def test_load_csv_and_preview(tmp_path):
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("a,b\n1,2\n3,4\n")

    df = load_csv(csv_path)

    assert list(df.columns) == ["a", "b"]
    assert df.shape == (2, 2)

    preview = preview_df(df)
    assert "| a" in preview
    assert "| 3" in preview
