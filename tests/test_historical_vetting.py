import numpy as np
from pandas.api.types import is_list_like

from scenariocompass import HistoricalVetting

VETING_INDICATOR = "Historical Vetting [SCI 2025]"


def assert_meta_values(df, cols, value):
    if not isinstance(value, str) and np.isnan(value):
        assert (df.meta[cols].isna()).all(axis=1).iloc[0]
    elif is_list_like(cols):
        assert (df.meta[cols] == value).all(axis=1).iloc[0]
    else:
        assert (df.meta[cols] == value).iloc[0]


def test_historical_vetting_pass(historical_vetting_df):
    """Check that historical vetting is passing as expected"""

    historical_vetting = HistoricalVetting()
    df = historical_vetting.apply(historical_vetting_df)

    assert_meta_values(df, VETING_INDICATOR, "passed")
    assert_meta_values(df, historical_vetting.criteria_names, "ok")


def test_historical_vetting_insufficient_reporting(historical_vetting_df):
    """Check that missing a vetting-variable yields 'insufficient_reporting' and n/a"""

    na_variable = "Primary Energy|Nuclear"
    df = historical_vetting_df.filter(variable=na_variable, keep=False)

    historical_vetting = HistoricalVetting()
    df = historical_vetting.apply(df)

    assert_meta_values(df, VETING_INDICATOR, "insufficient reporting")

    ok_cols = [
        col for col in historical_vetting.criteria_names if na_variable not in col
    ]
    assert_meta_values(df, ok_cols, "ok")

    # criteria columns where expected variable does not exist are marked as `n/a`
    na_cols = [col for col in historical_vetting.criteria_names if na_variable in col]
    assert_meta_values(df, na_cols, np.nan)


def test_historical_vetting_failed(historical_vetting_df):
    """Check that vetting-variable-value outside the range yields 'failed'"""

    df = historical_vetting_df.copy()
    # manually change a specific value
    df._data.iloc[1] = df._data.iloc[1] * 0.75

    historical_vetting = HistoricalVetting()
    df = historical_vetting.apply(df)

    assert_meta_values(df, VETING_INDICATOR, "failed")

    failed_col = "Historical Vetting|Emissions|CO2|Energy and Industrial Processes|2015"
    assert_meta_values(df, failed_col, "failed")

    ok_cols = [col for col in historical_vetting.criteria_names if col != failed_col]
    assert_meta_values(df, ok_cols, "ok")


def test_historical_vetting_failed_and_insufficient(historical_vetting_df):
    """Check that 'failed' takes precedence over 'insufficient_reporting'"""

    na_variable = "Primary Energy|Nuclear"
    df = historical_vetting_df.filter(variable=na_variable, keep=False)
    # manually change a specific value
    df._data.iloc[1] = df._data.iloc[1] * 0.75

    historical_vetting = HistoricalVetting()
    df = historical_vetting.apply(df)

    assert_meta_values(df, VETING_INDICATOR, "failed")

    failed_col = "Historical Vetting|Emissions|CO2|Energy and Industrial Processes|2015"
    assert_meta_values(df, failed_col, "failed")

    na_cols = [col for col in historical_vetting.criteria_names if na_variable in col]
    assert_meta_values(df, na_cols, np.nan)

    ok_cols = [
        col
        for col in historical_vetting.criteria_names
        if col != failed_col and col not in na_cols
    ]
    assert_meta_values(df, ok_cols, "ok")
