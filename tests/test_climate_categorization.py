import pandas as pd
import pandas.testing as pdt

from scenariocompass import ClimateCategorization

from .conftest import TEST_DATA_DIR


def test_assign_climate_category(climate_df):

    # import stylized subset of SCI v1.1 ensemble with one scenario per category

    # compute diagnostic meta-indicators from timeseries
    for p in ["Median", "67th Percentile"]:
        suffix = f"{p} [MAGICCv7.6.0a3]"
        v = "Climate Assessment|Surface Temperature (GSAT)|" + suffix

        for indicator, method_args in [
            ("Peak Warming", dict(method="max")),
            ("Warming in 2100", dict(year=2100)),
        ]:
            climate_df.set_meta_from_data(
                name=f"Climate Assessment|{indicator}|" + suffix,
                variable=v,
                **method_args,
            )

    # apply climate categorization
    climate_df = ClimateCategorization().apply(climate_df)

    # import expected meta-indicator dataframe
    exp = pd.read_csv(TEST_DATA_DIR / "climate-categorization-exp-meta.csv")
    cat_cols = [f"Climate Category|SCI 2025 [Tier {i}]" for i in ["I", "II", "III"]]
    pdt.assert_frame_equal(climate_df.meta[cat_cols].reset_index(), exp)
