from pathlib import Path

import numpy as np
import pandas as pd
import pyam

from scenariocompass import EmissionsDiagnostics


here = Path(__file__).parent.absolute()

EXP_META = pd.DataFrame(
    [
        ["MESSAGEix 1.1", "ENGAGE-NoPolicy", 5125.85, 6445.72, 0.0, np.nan, np.nan],
        ["REMIND 3.5", "Rescuing-1.5°C", 211.85, 841.31, 473.23, 2060., 2050.],
    ],
    columns=[
        "model",
        "scenario",
        "Emissions Diagnostics|Cumulative CO2 [2020-2100, Gt CO2]",
        "Emissions Diagnostics|Cumulative Kyoto Gases [2020-2100, Gt CO2e]",
        "Emissions Diagnostics|Cumulative CCS [2020-2100, Gt CO2]",
        "Emissions Diagnostics|Year of Net Zero|Kyoto Gases",
        "Emissions Diagnostics|Year of Net Zero|CO2",
    ],
)


def test_emissions_diagnostics():
    df = pyam.IamDataFrame(here / "data" / "emission_diagnostics.csv")

    emission_diagnostics = EmissionsDiagnostics()
    df = emission_diagnostics.apply(df)

    pd.testing.assert_frame_equal(
        df.meta, EXP_META.set_index(["model", "scenario"]), rtol=0.1,
    )