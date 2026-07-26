import numpy as np
import numpy.testing as npt
import pandas as pd
import pandas.testing as pdt
import pytest

from scenariocompass import EmissionsDiagnostics
from scenariocompass.emissions_diagnostics import (
    compute_cumulative_net_negative_emissions,
)


EXP_COLS = [
    "model",
    "scenario",
    "Emissions Diagnostics|Cumulative CO2 [2020-2100, Gt CO2]",
    "Emissions Diagnostics|Cumulative Kyoto Gases [2020-2100, Gt CO2e]",
    "Emissions Diagnostics|Cumulative CCS [2020-2100, Gt CO2]",
    "Emissions Diagnostics|Cumulative Net-Negative CO2 [2020-2100, Gt CO2]",
    "Emissions Diagnostics|Year of Net Zero|Kyoto Gases",
    "Emissions Diagnostics|Year of Net Zero|CO2",
]


EXP_META = pd.DataFrame(
    [
        ["MESSAGEix 1.1", "ENGAGE-NoPolicy", 5125.85, 6445.72, 0.0, 0, np.nan, np.nan],
        ["REMIND 3.5", "Rescuing-1.5°C", 211.85, 841.31, 473.23, -338.05, 2060, 2050],
    ],
    columns=EXP_COLS,
).set_index(["model", "scenario"])


def test_emissions_diagnostics(emissions_df):

    emission_diagnostics = EmissionsDiagnostics()
    emissions_df = emission_diagnostics.apply(emissions_df)

    pd.testing.assert_frame_equal(emissions_df.meta, EXP_META, rtol=0.1)


def test_emissions_diagnostics_short_horizon(emissions_df):
    emissions_df.filter(year=range(2020, 2080), inplace=True)

    emission_diagnostics = EmissionsDiagnostics()
    emissions_df = emission_diagnostics.apply(emissions_df)

    exp = EXP_META.copy()
    exp.iloc[0] = np.nan
    exp.iloc[1, 0:4] = np.nan
    pdt.assert_frame_equal(emissions_df.meta, exp)


def test_emissions_diagnostics_no_global_data(emissions_df):
    df = emissions_df.filter(region="Asia (R5)")

    emission_diagnostics = EmissionsDiagnostics()
    df = emission_diagnostics.apply(df)

    # fast pass, no meta columns added as part of the processing
    pdt.assert_frame_equal(df.meta, emissions_df.filter(model="MESSAGEix 1.1").meta)


def test_emissions_diagnostics_unknown_unit(emissions_df):
    emissions_df.rename(unit={"Mt CO2/yr": "foo"}, inplace=True)

    emission_diagnostics = EmissionsDiagnostics()
    match = "Invalid units for emissions diagnostics: foo"
    with pytest.raises(ValueError, match=match):
        emission_diagnostics.apply(emissions_df)


@pytest.mark.parametrize(
    "data, value",
    [
        # crossing threshold once/twice/three/four times
        ([100, -10, -20, -10, -30], -1024.5),
        ([100, -10, -20, -10, 10], -658.5),
        ([100, -10, 10, -10, -30], -523.5),
        ([100, -10, 10, -10, 10], -157.5),
        # reaching zero from below / from above but not crossing
        ([100, -10, 0, -10, 10], -259.0),
        ([100, -10, 10, 0, 10], -58.5),
    ],
)
def test_net_negative_emissions(data, value):

    x = pd.Series(data, index=[2020, 2040, 2060, 2080, 2100])
    npt.assert_almost_equal(compute_cumulative_net_negative_emissions(x), value)
