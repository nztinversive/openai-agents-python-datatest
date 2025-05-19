import pandas as pd  # type: ignore


def load_csv(path: str) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    return pd.read_csv(path)


def preview_df(df: pd.DataFrame) -> str:
    """Return first 5 rows of DataFrame as Markdown."""
    return str(df.head().to_markdown(index=False))
