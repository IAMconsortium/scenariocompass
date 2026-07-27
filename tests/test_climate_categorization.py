import logging

import numpy as np
import pandas.testing as pdt

from scenariocompass import ClimateCategorization

from .conftest import EXP_CLIMATE_META


def compute_meta_indicators(df):
    # compute diagnostic climate meta-indicators from timeseries
    for p in ["Median", "67th Percentile"]:
        suffix = f"{p} [MAGICCv7.6.0a3]"
        v = "Climate Assessment|Surface Temperature (GSAT)|" + suffix

        for indicator, method_args in [
            ("Peak Warming", dict(method="max")),
            ("Warming in 2100", dict(year=2100)),
        ]:
            df.set_meta_from_data(
                name=f"Climate Assessment|{indicator}|" + suffix,
                variable=v,
                **method_args,
            )
    return df


def test_assign_climate_category(climate_df):

    # start with stylized subset of SCI v1.1 ensemble with one scenario per category
    climate_df = compute_meta_indicators(climate_df)

    # add a miscellaneous climate category assignment, which shall be removed by
    # calling the ClimateCategorization `apply()` method
    climate_df.meta["Climate Category|SCI 2025 [foo]"] = 1

    # apply climate categorization
    climate_df = ClimateCategorization().apply(climate_df)

    # check that the miscellaneous category-column was removed
    assert "Climate Category|SCI 2025 [foo]" not in climate_df.meta.columns

    # import expected meta-indicator dataframe
    cat_cols = [f"Climate Category|SCI 2025 [Tier {i}]" for i in ["I", "II", "III"]]
    pdt.assert_frame_equal(climate_df.meta[cat_cols], EXP_CLIMATE_META)


def test_assign_climate_category_missing_meta_columns(climate_df, caplog):

    # calling the climate categorization if meta-indicators do not exist is skipped
    climate_df = compute_meta_indicators(climate_df)
    climate_df.meta.drop(
        columns=[
            "Climate Assessment|Peak Warming|Median [MAGICCv7.6.0a3]",
            "Climate Assessment|Warming in 2100|67th Percentile [MAGICCv7.6.0a3]",
        ],
        inplace=True,
    )

    climate_df = ClimateCategorization().apply(climate_df)

    assert caplog.record_tuples == [
        (
            "scenariocompass.climate_categorization",  # namespacing
            logging.WARNING,  # level
            (
                "Missing required meta columns for all scenarios:\n"
                " - Climate Assessment|Peak Warming|Median [MAGICCv7.6.0a3]\n"
                " - Climate Assessment|Warming in 2100|67th Percentile [MAGICCv7.6.0a3]"
            ),
        )
    ]
    assert "Climate Category|SCI 2025 [Tier 1]" not in climate_df.meta.columns


def test_assign_climate_category_missing_run(climate_df, caplog):

    # remove one required meta-indicator for one scenario
    climate_df = compute_meta_indicators(climate_df)
    index = ("GEM-E3 V2021", "ENGAGE-NPi2020-500")
    climate_df.meta.loc[
        index, "Climate Assessment|Peak Warming|Median [MAGICCv7.6.0a3]"
    ] = None

    climate_df = ClimateCategorization().apply(climate_df)

    assert caplog.record_tuples == [
        (
            "scenariocompass.climate_categorization",  # namespacing
            logging.WARNING,  # level
            "Missing meta indicators for 1 scenarios."
        )
    ]

    # check that this senario does not have a climate category assignment
    exp = EXP_CLIMATE_META.copy()
    cat_cols = [f"Climate Category|SCI 2025 [Tier {i}]" for i in ["I", "II", "III"]]
    exp.loc[index, cat_cols] = np.nan
    pdt.assert_frame_equal(climate_df.meta[cat_cols], exp)
