import pandas as pd
from fcast.pipeline.validator import validate_long_df

def test_validate_long_df_ok():
    df = pd.DataFrame({
        "unique_id": ["N1","N1","N2","N2"],
        "ds": pd.to_datetime(["2020-01-01","2020-01-08","2020-01-01","2020-01-08"]),
        "y": [1,2,3,4],
    })
    v = validate_long_df(df)
    assert len([x for x in v if x.severity=="error"]) == 0
