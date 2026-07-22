import logging

import pandas as pd

from nomenclature.processor import Processor
from pyam import IamDataFrame


logger = logging.getLogger(__name__)


required_meta_columns_mapping = {
    "Climate Assessment|Peak Warming|Median [MAGICCv7.6.0a3]": "peak_p50",
    "Climate Assessment|Peak Warming|67th Percentile [MAGICCv7.6.0a3]": "peak_p67",
    "Climate Assessment|Warming in 2100|Median [MAGICCv7.6.0a3]": "eoc_p50",
    "Climate Assessment|Warming in 2100|67th Percentile [MAGICCv7.6.0a3]": "eoc_p67",
}

temperature_p50 = (
    "Climate Assessment|Surface Temperature (GSAT)|Median [MAGICCv7.6.0a3]"
)
ghg_emissions = "Climate Assessment|Harmonized and Infilled|Emissions|Kyoto Gases [AR6GWP100] [gcages 0.14]"


tier_2_mapping = {
    "GW0": "GW0*",
    "GW1": "GW1*",
    "GW2a": ["GW2-I", "GW2-II"],
    "GW2b": "GW2-III*",
    "GW3a": "GW3-I",
    "GW3b": "GW3-II*",
    "GW4": "GW4*",
    "GW5": "GW5*",
    "GW6": "GW6",
    "GW7": "GW7",
    "GW8": "GW8",
}


class ClimateCategorization(Processor):
    category_name: str = "Climate Category|SCI 2025"

    def apply(self, df: IamDataFrame) -> IamDataFrame:

        df = self.reset_apply(df)

        if missing_meta_columns := [
            col
            for col in required_meta_columns_mapping.keys()
            if col not in df.meta.columns
        ]:
            logger.warning(
                "Missing required meta columns: " + ", ".join(missing_meta_columns)
            )
            return df

        meta = df.meta[required_meta_columns_mapping.keys()].rename(
            columns=required_meta_columns_mapping
        )
        decreasing_temperature = pd.Series(
            (
                df.filter(variable=temperature_p50)
                .subtract(2100, 2090, "0", axis="year")
                .data.set_index(["model", "scenario"])
            )["value"]
            < 0,
            name="decreasing_temperature",
        )
        net_negative_ghg = pd.Series(
            (
                df.filter(variable=ghg_emissions, year=2100).data.set_index(
                    ["model", "scenario"]
                )
            )["value"]
            < 0,
            name="net_negative_ghg",
        )
        meta = meta.merge(
            decreasing_temperature, left_index=True, right_index=True
        ).merge(net_negative_ghg, left_index=True, right_index=True)

        category_3 = self.category_name + " [Tier III]"

        meta = _assign_sci_category(
            df, meta, category_3, "GW0a", 1.5, 50, 1.5, 50, net_negative_ghg=True
        )
        meta = _assign_sci_category(
            df, meta, category_3, "GW0b", 1.5, 50, 1.5, 50, net_negative_ghg=False
        )
        meta = _assign_sci_category(
            df, meta, category_3, "GW1a", 1.6, 50, 1.5, 50, net_negative_ghg=True
        )
        meta = _assign_sci_category(
            df, meta, category_3, "GW1b", 1.6, 50, 1.5, 50, net_negative_ghg=False
        )
        meta = _assign_sci_category(df, meta, category_3, "GW2-I", 1.7, 50, 1.5, 67)
        meta = _assign_sci_category(df, meta, category_3, "GW2-II", 1.7, 50, 1.5, 50)
        meta = _assign_sci_category(
            df, meta, category_3, "GW2-IIIa", 1.7, 50, 1.7, 50, net_negative_ghg=True
        )
        meta = _assign_sci_category(
            df,
            meta,
            category_3,
            "GW2-IIIb",
            1.7,
            50,
            1.7,
            50,
            decreasing_temperature=True,
        )
        meta = _assign_sci_category(
            df,
            meta,
            category_3,
            "GW2-IIIc",
            1.7,
            50,
            1.7,
            50,
            decreasing_temperature=False,
        )
        meta = _assign_sci_category(df, meta, category_3, "GW3-I", 2.0, 67, 1.5, 50)
        meta = _assign_sci_category(
            df, meta, category_3, "GW3-IIa", 2.0, 67, 2.0, 67, net_negative_ghg=True
        )
        meta = _assign_sci_category(
            df,
            meta,
            category_3,
            "GW3-IIb",
            2.0,
            67,
            2.0,
            67,
            decreasing_temperature=True,
        )
        meta = _assign_sci_category(
            df,
            meta,
            category_3,
            "GW3-IIc",
            2.0,
            67,
            2.0,
            67,
            decreasing_temperature=False,
        )
        meta = _assign_sci_category(df, meta, category_3, "GW4-I", 2.0, 50, 1.7, 50)
        meta = _assign_sci_category(
            df, meta, category_3, "GW4-IIa", 2.0, 50, 2.0, 50, net_negative_ghg=True
        )
        meta = _assign_sci_category(
            df,
            meta,
            category_3,
            "GW4-IIb",
            2.0,
            50,
            2.0,
            50,
            decreasing_temperature=True,
        )
        meta = _assign_sci_category(
            df,
            meta,
            category_3,
            "GW4-IIc",
            2.0,
            50,
            2.0,
            50,
            decreasing_temperature=False,
        )
        meta = _assign_sci_category(
            df, meta, category_3, "GW5a", 2.5, 50, 2.5, 50, decreasing_temperature=True
        )
        meta = _assign_sci_category(
            df, meta, category_3, "GW5b", 2.5, 50, 2.5, 50, decreasing_temperature=False
        )
        meta = _assign_sci_category(df, meta, category_3, "GW6", 3.0, 50, 3.0, 50)
        meta = _assign_sci_category(df, meta, category_3, "GW7", 3.5, 50, 3.5, 50)
        df.set_meta(name=category_3, meta="GW8", index=meta.index)

        category_2 = self.category_name + " [Tier II]"
        for name, category in tier_2_mapping.items():
            df.set_meta(
                name=category_2,
                meta=name,
                index=df.filter(**{category_3: category}).index,
            )

        category_1 = self.category_name + " [Tier I]"
        for i in range(0, 9):
            df.set_meta(
                name=category_1,
                meta=f"GW{i}",
                index=df.filter(**{category_3: f"GW{i}*"}).index,
            )

        return df

    def reset_apply(self, df: IamDataFrame) -> IamDataFrame:
        category_cols = [f"{self.category_name} [Tier {i}]" for i in ["I", "II", "III"]]

        if existing_cols := [col for col in category_cols if col in df.meta.columns]:
            logger.info(f"Resetting {len(existing_cols)} climate category indicators")
            df.meta.drop(existing_cols, axis=1, inplace=True)
        else:
            logger.info("No climate category indicators to reset")

        return df


def _assign_sci_category(
    df,
    meta,
    name,
    value,
    peak_threshold,
    peak_pecentile,
    eoc_threshold,
    eoc_percentile,
    decreasing_temperature=None,
    net_negative_ghg=None,
):

    match = (meta[f"peak_p{peak_pecentile}"] < peak_threshold) & (
        meta[f"eoc_p{eoc_percentile}"] < eoc_threshold
    )
    if decreasing_temperature is not None:
        match = match[match] & (meta.decreasing_temperature == decreasing_temperature)
    if net_negative_ghg is not None:
        match = match[match] & (meta.net_negative_ghg == net_negative_ghg)

    df.set_meta(name=name, meta=value, index=match[match].index)

    return meta[~match]
