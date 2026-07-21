import logging

from nomenclature.processor import Processor
import pyam
from pyam import IamDataFrame

logger = logging.getLogger(__name__)


class EmissionsDiagnostics(Processor):
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

        df = self.reset_apply(df)

        _df = df.filter(**self.input_data, keep=True, inplace=False)
        if _df.empty:
            return df

        invalid_units = set(_df.unit).difference(["Mt CO2/yr", "Mt CO2-equiv/yr"])
        if invalid_units:
            raise ValueError(
                "Invalid units for emissions diagnostics: " + ", ".join(invalid_units)
            )

        # compute indicators for cumulative emissions and CCS
        for name, variable in {
            "Cumulative CO2 [2020-2100, Gt CO2]": "Emissions|CO2",
            "Cumulative Kyoto Gases [2020-2100, Gt CO2e]": "Emissions|Kyoto Gases",
            "Cumulative CCS [2020-2100, Gt CO2]": "Carbon Capture|Geological Storage",
        }.items():
            df.set_meta(
                name="Emissions Diagnostics|" + name,
                meta=compute_cumulative_eoc(_df.filter(variable=variable)),
            )

        df.set_meta(
            name=f"{self.prefix}|Cumulative Net-Negative CO2 [2020-2100, Gt CO2]",
            meta=(
                _df.filter(variable="Emissions|CO2")
                .timeseries()
                .apply(compute_cumulative_net_negative_emissions, raw=False, axis=1)
                / 1000
            ),
        )

        for species in ["Kyoto Gases", "CO2"]:
            df.set_meta(
                name=f"{self.prefix}|Year of Net Zero|{species}",
                meta=(
                    _df.filter(variable=f"Emissions|{species}")
                    .timeseries()
                    .apply(year_of_netzero, raw=False, axis=1)
                ),
            )

        return df

    def reset_apply(self, df: IamDataFrame) -> IamDataFrame:

        cols = [col for col in df.meta.columns if col.startswith(self.prefix + "|")]
        if cols:
            logger.info(f"Resetting {len(cols)} '{self.prefix}' meta-indidators")
            df.meta.drop(cols, axis=1, inplace=True)

        return df


def compute_cumulative_eoc(df):
    if df.empty:
        return None

    return (
        df.timeseries().apply(
            lambda x: pyam.timeseries.cumulative(x, 2020, 2100), raw=False, axis=1
        )
        / 1000
    )


def compute_cumulative_net_negative_emissions(x):
    if 2100 not in x.index:
        return None

    return _compute_cumulative(x, 0, pyam.timeseries.cross_threshold(x))


def _compute_cumulative(x, value, zero_years):
    if len(zero_years) == 0:
        return value
    elif len(zero_years) == 1:
        return value + pyam.timeseries.cumulative(x, zero_years[0], 2100)
    else:
        value += pyam.timeseries.cumulative(x, zero_years[0], zero_years[1])
        return _compute_cumulative(x, value, zero_years[2:])


def year_of_netzero(x):
    net_zero = pyam.timeseries.cross_threshold(x)

    # this is special handling for scenarios that reach net-zero assymptotically
    if not net_zero:
        net_zero = pyam.timeseries.cross_threshold(x, threshold=1)

    if net_zero:
        return net_zero[0]
