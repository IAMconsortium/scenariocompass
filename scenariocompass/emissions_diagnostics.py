import logging

import numpy as np
import pyam
from nomenclature.processor import Processor
from pyam import IamDataFrame

logger = logging.getLogger(__name__)


class EmissionsDiagnostics(Processor):
    """Diagnostics for emissions indicators."""

    prefix: str = "Emissions Diagnostics"
    input_data: dict[str, list[str]] = dict(
        variable=[
            "Emissions|CO2",
            "Emissions|Kyoto Gases",
            "Carbon Capture|Geological Storage",
        ],
        region=["World"],
    )
    output_meta: list[str] = [
        "Emissions Diagnostics|Cumulative CO2 [2020-2100, Gt CO2]",
        "Emissions Diagnostics|Cumulative Kyoto Gases [2020-2100, Gt CO2e]",
        "Emissions Diagnostics|Cumulative CCS [2020-2100, Gt CO2]",
        "Emissions Diagnostics|Cumulative Net-Negative CO2 [2020-2100, Gt CO2]"
        "Emissions Diagnostics|Year of Net Zero|Kyoto Gases",
        "Emissions Diagnostics|Year of Net Zero|CO2",
    ]

    def apply(self, df: pyam.IamDataFrame):
        """Compute emissions diagnostics for the scenarios."""
        df = self.reset_apply(df)

        with pyam.utils.adjust_log_level():
            _df = df.filter(**self.input_data)
        if _df.empty:
            logger.warning(
                "Skipping emissions diagnostics because of missing required variables"
            )
            return df

        invalid_units = set(_df.unit).difference(["Mt CO2/yr", "Mt CO2-equiv/yr"])
        if invalid_units:
            raise ValueError(
                "Invalid units for emissions diagnostics: " + ", ".join(invalid_units)
            )

        for variable, indicator_mapping in [
            (
                "Emissions|CO2",
                {
                    "Cumulative CO2 [2020-2100, Gt CO2]": compute_cumulative_2100,
                    "Cumulative Net-Negative CO2 [2020-2100, Gt CO2]": compute_cumulative_net_negative_emissions,
                    "Year of Net Zero|CO2": year_of_netzero,
                },
            ),
            (
                "Emissions|Kyoto Gases",
                {
                    "Cumulative Kyoto Gases [2020-2100, Gt CO2e]": compute_cumulative_2100,
                    "Year of Net Zero|Kyoto Gases": year_of_netzero,
                },
            ),
            (
                "Carbon Capture|Geological Storage",
                {
                    "Cumulative CCS [2020-2100, Gt CO2]": compute_cumulative_2100,
                },
            ),
        ]:
            if variable not in _df.variable:
                logger.warning(
                    f"Missing variable '{variable}' for emissions diagnostics"
                )
                continue

            _data = _df.filter(variable=variable).timeseries()
            for indicator, func in indicator_mapping.items():
                df.set_meta(
                    name=f"{self.prefix}|{indicator}",
                    meta=(_data.apply(lambda x: func(x), raw=False, axis=1)),
                )

        return df

    def reset_apply(self, df: IamDataFrame) -> IamDataFrame:
        """Remove all meta-indicators for the emissions diagnostics."""
        cols = [col for col in df.meta.columns if col.startswith(self.prefix + "|")]
        if cols:
            logger.info(f"Resetting {len(cols)} '{self.prefix}' meta-indidators")
            df.meta.drop(cols, axis=1, inplace=True)

        return df


def compute_cumulative_2100(x):
    if 2100 not in x.index:
        return np.nan

    return pyam.timeseries.cumulative(x, 2020, 2100) / 1000


def compute_cumulative_net_negative_emissions(x):
    if 2100 not in x.index:
        return np.nan

    return (
        _compute_cumulative_below_zero(x, 0, pyam.timeseries.cross_threshold(x)) / 1000
    )


def _compute_cumulative_below_zero(x, value, zero_years):
    if len(zero_years) == 0:
        return value
    elif len(zero_years) == 1:
        return value + pyam.timeseries.cumulative(x, zero_years[0], 2100)
    else:
        value += pyam.timeseries.cumulative(x, zero_years[0], zero_years[1])
        return _compute_cumulative_below_zero(x, value, zero_years[2:])


def year_of_netzero(x):
    net_zero = pyam.timeseries.cross_threshold(x)

    # this is special handling for scenarios that reach net-zero assymptotically
    if not net_zero:
        net_zero = pyam.timeseries.cross_threshold(x, threshold=1)

    if net_zero:
        return int(net_zero[0])
    return None
