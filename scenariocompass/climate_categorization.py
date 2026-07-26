import logging
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from nomenclature.processor import Processor
from pyam import IamDataFrame


logger = logging.getLogger(__name__)


REQUIRED_META_COLUMNS = {
    "Climate Assessment|Peak Warming|Median [MAGICCv7.6.0a3]": "peak_p50",
    "Climate Assessment|Peak Warming|67th Percentile [MAGICCv7.6.0a3]": "peak_p67",
    "Climate Assessment|Warming in 2100|Median [MAGICCv7.6.0a3]": "eoc_p50",
    "Climate Assessment|Warming in 2100|67th Percentile [MAGICCv7.6.0a3]": "eoc_p67",
}

TEMPERATURE_P50 = (
    "Climate Assessment|Surface Temperature (GSAT)|Median [MAGICCv7.6.0a3]"
)
GHG_EMISSIONS = "Climate Assessment|Harmonized and Infilled|Emissions|Kyoto Gases [AR6GWP100] [gcages 0.14]"


TIER_2_MAPPING = {
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

# scenarios that do not match any rule below are categorized as this default
DEFAULT_TIER_3_CATEGORY = "GW8"


@dataclass(frozen=True)
class CategoryRule:
    """A single Tier III SCI 2025 category classification rule.

    A scenario matches the rule if its peak/end-of-century warming indicators are below
    the given thresholds, and (if specified) it exhibits decreasing-temperature and
    net-negative-GHG at the end of the century.
    """

    name: str
    peak_threshold: float
    peak_percentile: int
    eoc_threshold: float
    eoc_percentile: int
    decreasing_temperature: Optional[bool] = None
    net_negative_ghg: Optional[bool] = None


TIER_3_RULES = [
    CategoryRule("GW0a", 1.5, 50, 1.5, 50, net_negative_ghg=True),
    CategoryRule("GW0b", 1.5, 50, 1.5, 50, net_negative_ghg=False),
    CategoryRule("GW1a", 1.6, 50, 1.5, 50, net_negative_ghg=True),
    CategoryRule("GW1b", 1.6, 50, 1.5, 50, net_negative_ghg=False),
    CategoryRule("GW2-I", 1.7, 50, 1.5, 67),
    CategoryRule("GW2-II", 1.7, 50, 1.5, 50),
    CategoryRule("GW2-IIIa", 1.7, 50, 1.7, 50, net_negative_ghg=True),
    CategoryRule("GW2-IIIb", 1.7, 50, 1.7, 50, decreasing_temperature=True),
    CategoryRule("GW2-IIIc", 1.7, 50, 1.7, 50, decreasing_temperature=False),
    CategoryRule("GW3-I", 2.0, 67, 1.5, 50),
    CategoryRule("GW3-IIa", 2.0, 67, 2.0, 67, net_negative_ghg=True),
    CategoryRule("GW3-IIb", 2.0, 67, 2.0, 67, decreasing_temperature=True),
    CategoryRule("GW3-IIc", 2.0, 67, 2.0, 67, decreasing_temperature=False),
    CategoryRule("GW4-I", 2.0, 50, 1.7, 50),
    CategoryRule("GW4-IIa", 2.0, 50, 2.0, 50, net_negative_ghg=True),
    CategoryRule("GW4-IIb", 2.0, 50, 2.0, 50, decreasing_temperature=True),
    CategoryRule("GW4-IIc", 2.0, 50, 2.0, 50, decreasing_temperature=False),
    CategoryRule("GW5a", 2.5, 50, 2.5, 50, decreasing_temperature=True),
    CategoryRule("GW5b", 2.5, 50, 2.5, 50, decreasing_temperature=False),
    CategoryRule("GW6", 3.0, 50, 3.0, 50),
    CategoryRule("GW7", 3.5, 50, 3.5, 50),
]


class ClimateCategorization(Processor):
    category_name: str = "Climate Category|SCI 2025"

    def apply(self, df: IamDataFrame) -> IamDataFrame:
        """Apply the climate categorization to the scenarios."""

        df = self.reset_apply(df)

        meta = _compute_diagnostics(df)
        if meta is None:
            return df

        tier_3 = f"{self.category_name} [Tier III]"
        for rule in TIER_3_RULES:
            meta = _assign_sci_category(df, meta, tier_3, rule)
        df.set_meta(name=tier_3, meta=DEFAULT_TIER_3_CATEGORY, index=meta.index)

        tier_2 = f"{self.category_name} [Tier II]"
        for name, components in TIER_2_MAPPING.items():
            df.set_meta(
                name=tier_2,
                meta=name,
                index=df.filter(**{tier_3: components}).index,
            )

        tier_1 = f"{self.category_name} [Tier I]"
        for i in range(9):
            df.set_meta(
                name=tier_1,
                meta=f"GW{i}",
                index=df.filter(**{tier_2: f"GW{i}*"}).index,
            )

        return df

    def reset_apply(self, df: IamDataFrame) -> IamDataFrame:
        """Remove all meta indicators for the climate category name"""
        reset_cols = [
            col for col in df.meta.columns if col.startswith(self.category_name)
        ]

        if reset_cols:
            logger.info(f"Resetting {len(reset_cols)} climate category indicators")
            df.meta.drop(reset_cols, axis=1, inplace=True)

        return df


def _compute_diagnostics(df: IamDataFrame) -> Optional[pd.DataFrame]:
    """Build the meta dataframe of diagnostic indicators used for categorization.

    Returns None (and logs a warning) if required meta columns are missing.
    """
    missing_meta_columns = [
        col for col in REQUIRED_META_COLUMNS if col not in df.meta.columns
    ]
    if missing_meta_columns:
        logger.warning(
            "Missing required meta columns:\n - " + "\n - ".join(missing_meta_columns)
        )
        return None

    meta = df.meta[list(REQUIRED_META_COLUMNS)].rename(
        columns=REQUIRED_META_COLUMNS
    )

    meta["decreasing_temperature"] = _value_below_zero(
        df.filter(variable=TEMPERATURE_P50).subtract(2100, 2090, "0", axis="year")
    )
    meta["net_negative_ghg"] = _value_below_zero(
        df.filter(variable=GHG_EMISSIONS, year=2100)
    )

    return meta


def _value_below_zero(df: IamDataFrame) -> pd.Series:
    """Return a boolean Series indexed by (model, scenario) of `value < 0`."""
    return df.data.set_index(["model", "scenario"])["value"] < 0


def _assign_sci_category(
    df: IamDataFrame, meta: pd.DataFrame, name: str, rule: CategoryRule
) -> pd.DataFrame:
    """Set meta indicator to `rule.name` for all scenarios in `meta` matching `rule`.

    Returns the subset of `meta` that did not match, for evaluation against
    subsequent rules.
    """
    match = (meta[f"peak_p{rule.peak_percentile}"] < rule.peak_threshold) & (
        meta[f"eoc_p{rule.eoc_percentile}"] < rule.eoc_threshold
    )
    if rule.decreasing_temperature is not None:
        match &= meta.decreasing_temperature == rule.decreasing_temperature
    if rule.net_negative_ghg is not None:
        match &= meta.net_negative_ghg == rule.net_negative_ghg

    df.set_meta(name=name, meta=rule.name, index=meta.index[match])

    return meta[~match]
