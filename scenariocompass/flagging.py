import logging

from pyam import IamDataFrame
from nomenclature.processor import Processor, DataValidator
from pydantic import model_validator

from scenariocompass.utils import parse_validators

logger = logging.getLogger(__name__)


META_CCS_CONCERN_NAME = (
    "Sustainability Concern|Exceeding Prudent Limit For Geological Carbon Storage|World"
)


class ConcernValidator(Processor):
    validators: list[DataValidator] = []

    @property
    def criteria_names(self) -> list[str]:
        """Get the names of flagging criteria"""
        names = list()
        for validator in self.validators:
            for item in validator.criteria_items:
                names.append(item.name)
        return names

    def apply(self, df: IamDataFrame) -> IamDataFrame:
        for validator in self.validators:
            validator.apply(df)
        return df

    def reset_apply(self, df: IamDataFrame) -> IamDataFrame:
        flagging_cols = [col for col in self.criteria_names if col in df.meta.columns]

        if flagging_cols:
            logger.info(f"Resetting {len(flagging_cols)} flag criteria")
            df.meta.drop(flagging_cols, axis=1, inplace=True)

        return df


class FeasibilityValidator(ConcernValidator):
    pattern: str = "feasible_*.yaml"
    reassign_capacity_flags: bool = False

    @model_validator(mode="before")
    @classmethod
    def parse_validators(cls, values):
        return parse_validators(values, default_pattern="feasible_*.yaml")

    def apply(self, df: IamDataFrame) -> IamDataFrame:

        # Apply standard validators
        df = super().apply(df)

        # Apply custom validator
        if self.reassign_capacity_flags:
            df = _reassign_capacity_flags(
                df,
                energy_variable="Secondary Energy|Electricity|Solar",
                year=2030,
                meta_column="Feasibility Concern|Solar PV Capacity|World|2030",
            )

        return df


class SustainabilityValidator(ConcernValidator):
    pattern: str = "sustainable_*.yaml"

    @model_validator(mode="before")
    @classmethod
    def parse_validators(cls, values):
        return parse_validators(values, default_pattern="sustainable_*.yaml")

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

    failed_scenarios = df.filter(
        variable=energy_variable, year=year, **{meta_column: ["high"]}
    )._data

    reassigned_scenarios = failed_scenarios[
        failed_scenarios > plausible_minimum_energy
    ].index

    if not reassigned_scenarios.empty:
        logger.info(
            f"Reassigned indicator '{meta_column}' for {len(reassigned_scenarios)} of "
            f"{len(failed_scenarios)} scenarios that initially failed validation\n"
            f"Updated lower bound for '{energy_variable}' > {plausible_minimum_energy}"
        )
        df.set_meta(
            name=meta_column,
            meta="medium",
            index=reassigned_scenarios,
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
