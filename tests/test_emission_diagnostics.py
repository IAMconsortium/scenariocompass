from pathlib import Path

import numpy as np
import pandas as pd
import pyam
import pytest

from scenariocompass import EmissionsDiagnostics


here = Path(__file__).parent.absolute()


EXP_COLS = [
    "model",
    "scenario",
    "Emissions Diagnostics|Cumulative CO2 [2020-2100, Gt CO2]",
    "Emissions Diagnostics|Cumulative Kyoto Gases [2020-2100, Gt CO2e]",
    "Emissions Diagnostics|Cumulative CCS [2020-2100, Gt CO2]",
    "Emissions Diagnostics|Year of Net Zero|Kyoto Gases",
    "Emissions Diagnostics|Year of Net Zero|CO2",
]


EXP_META = pd.DataFrame(
    [
        ["MESSAGEix 1.1", "ENGAGE-NoPolicy", 5125.85, 6445.72, 0.0, np.nan, np.nan],
        ["REMIND 3.5", "Rescuing-1.5°C", 211.85, 841.31, 473.23, 2060.0, 2050.0],
    ],
    columns=EXP_COLS,
).set_index(["model", "scenario"])


TEST_DF = pyam.IamDataFrame(here / "data" / "emission_diagnostics.csv")


def test_emissions_diagnostics():
    df = TEST_DF.copy()

    emission_diagnostics = EmissionsDiagnostics()
    df = emission_diagnostics.apply(df)

    pd.testing.assert_frame_equal(df.meta, EXP_META, rtol=0.1)


def test_emissions_diagnostics_short_horizon():
    df = TEST_DF.filter(year=range(2020, 2080))

    emission_diagnostics = EmissionsDiagnostics()
    df = emission_diagnostics.apply(df)

    exp = EXP_META.copy()
    exp.iloc[0] = np.nan
    exp.iloc[1, 0:3] = np.nan
    pd.testing.assert_frame_equal(df.meta, exp)


def test_emissions_diagnostics_no_global_data():
    df = TEST_DF.filter(region="Asia (R5)")

    emission_diagnostics = EmissionsDiagnostics()
    df = emission_diagnostics.apply(df)

    # fast pass, no meta columns added as part of the processing
    pd.testing.assert_frame_equal(df.meta, TEST_DF.filter(model="MESSAGEix 1.1").meta)


def test_emissions_diagnostics_unknown_unit():
    df = TEST_DF.rename(unit={"Mt CO2/yr": "foo"})

    emission_diagnostics = EmissionsDiagnostics()
    match = "Invalid units for emissions diagnostics: foo"
    with pytest.raises(ValueError, match=match):
        emission_diagnostics.apply(df)
