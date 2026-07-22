import logging
from pyam import IamDataFrame
from pyam.utils import adjust_log_level

from scenariocompass.validation import GroupedValidator

logger = logging.getLogger(__name__)


META_CCS_CONCERN_NAME = (
    "Sustainability Concern|Exceeding Prudent Limit For Geological Carbon Storage|World"
)


class FeasibilityValidator(GroupedValidator):
    prefix: str = "Feasibility Concern"
    pattern: str = "feasible_*.yaml"
    reassign_capacity_flags: bool = False

    def apply(self, df: IamDataFrame) -> IamDataFrame:

        # Apply standard validators
        df = super().apply(df)

        # Apply custom validator
        if self.reassign_capacity_flags:
            df = _reassign_capacity_flags(
                df,
                energy_variable="Secondary Energy|Electricity|Solar",
                capacity_variable="Capacity|Electricity|Solar",
                capacity_upper_bound=10896.0,
                year=2030,
                meta_column="Feasibility Concern|Solar PV Capacity|World|2030",
            )

        return df


class SustainabilityValidator(GroupedValidator):
    prefix: str = "Sustainability Concern"
    pattern: str = "sustainable_*.yaml"

    @property
    def criteria_names(self) -> list[str]:
        return super().criteria_names + [META_CCS_CONCERN_NAME]

    def apply(self, df: IamDataFrame) -> IamDataFrame:

        # Apply standard validators
        df = super().apply(df)

        # Apply custom validator
        df = _apply_cumululative_ccs_concern(df)

        return df


def _reassign_capacity_flags(
    df: IamDataFrame,
    energy_variable: str,
    capacity_variable: str,
    capacity_upper_bound: float,
    year: int,
    meta_column: str,
) -> IamDataFrame:

    plausible_minimum_energy = (
        df.filter(
            variable=energy_variable, year=year, **{meta_column: ["ok", "medium"]}
        )
        ._data.min()
        .round(2)
    )

    high_concern_scenarios = df.filter(
        variable=[energy_variable, capacity_variable],
        year=year,
        **{meta_column: ["high"]},
    )
    with adjust_log_level():
        high_concern_scenarios.validate(
            variable=energy_variable,
            lower_bound=plausible_minimum_energy,
            exclude_on_fail=True,
        )
        high_concern_scenarios.validate(
            variable=capacity_variable,
            upper_bound=capacity_upper_bound,
            exclude_on_fail=True,
        )
        reassigned_df = high_concern_scenarios.filter(exclude=False)

    if not reassigned_df.empty:
        logger.info(
            f"Reassigned indicator '{meta_column}' to *medium* for {len(reassigned_df.index)} of "
            f"{len(high_concern_scenarios.index)} scenarios that initially failed validation\n"
            f"Updated lower bound for '{energy_variable}' > {plausible_minimum_energy}"
        )
        df.set_meta(
            name=meta_column,
            meta="medium",
            index=reassigned_df.index,
        )
    return df


def _apply_cumululative_ccs_concern(df: IamDataFrame) -> IamDataFrame:
    """Set sustainability flag if cumulative CCS is exceeding prudent limit"""

    ccs_value_column = "Emissions Diagnostics|Cumulative CCS [2020-2100, Gt CO2]"

    if META_CCS_CONCERN_NAME in df.meta.columns:
        df.meta.drop(columns=META_CCS_CONCERN_NAME, inplace=True)

    if ccs_value_column not in df.meta.columns:
        logger.warning(
            "No meta-indicator for cumulative CCS, skipping indicator '"
            + ccs_value_column
            + "'"
        )
    else:
        for value, match in (
            ("ok", ~df.meta[ccs_value_column].isna()),
            ("medium", df.meta[ccs_value_column] > 1290),
            ("high", df.meta[ccs_value_column] > 1460),
        ):
            df.set_meta(
                name=META_CCS_CONCERN_NAME,
                meta=value,
                index=df.meta[match].index,
            )
    return df
