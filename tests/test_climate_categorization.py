from pathlib import Path

import pandas as pd
import pandas.testing as pdt
from pyam import IamDataFrame

from scenariocompass import ClimateCategorization

TEST_DATA_DIR = Path(__file__).parent.absolute() / "data"


def test_assign_climate_category():
    # import stylized subset of SCI v1.1 ensemble with one scenario per category
    test_df = IamDataFrame(TEST_DATA_DIR / "climate-categorization-test-data.csv")

    # compute diagnostic meta-indicators from timeseries
    for p in ["Median", "67th Percentile"]:
        suffix = f"{p} [MAGICCv7.6.0a3]"
        v = "Climate Assessment|Surface Temperature (GSAT)|" + suffix

        for indicator, method_args in [
            ("Peak Warming", dict(method="max")),
            ("Warming in 2100", dict(year=2100)),
        ]:
            test_df.set_meta_from_data(
                name=f"Climate Assessment|{indicator}|" + suffix,
                variable=v,
                **method_args,
            )

    # apply climate categorization
    test_df = ClimateCategorization().apply(test_df)

    # import expected meta-indicator dataframe
    exp = pd.read_csv(TEST_DATA_DIR / "climate-categorization-exp-meta.csv")
    category_cols = [f"Climate Category|SCI 2025 [Tier {i}]" for i in ["I", "II"]]
    pdt.assert_frame_equal(test_df.meta[category_cols].reset_index(), exp)