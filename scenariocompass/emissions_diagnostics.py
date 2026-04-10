import nomenclature
from nomenclature import RequiredDataValidator
from nomenclature.processor import Processor

import pyam


class EmissionsDiagnostics(Processor):
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
        "Emissions Diagnostics|Year of Net Zero|Kyoto Gases",
        "Emissions Diagnostics|Year of Net Zero|CO2",
    ]

    def apply(self, df: pyam.IamDataFrame):

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

        # TODO Emissions Diagnostics|Cumulative Net-Negative CO2 [2020-2100, Gt CO2]",

        for species in ["Kyoto Gases", "CO2"]:
            df.set_meta(
                name=f"Emissions Diagnostics|Year of Net Zero|{species}",
                meta=_df.filter(variable=f"Emissions|{species}")
                .timeseries()
                .apply(year_of_netzero, raw=False, axis=1),
            )

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


def year_of_netzero(x):
    net_zero = pyam.timeseries.cross_threshold(x)

    # this is special handling for scenarios that reach net-zero assymptotically
    if not net_zero:
        net_zero = pyam.timeseries.cross_threshold(x, threshold=1)

    if net_zero:
        return net_zero[0]
