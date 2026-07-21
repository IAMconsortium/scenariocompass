import logging

from nomenclature.processor.data_validator import WarningEnum
from pyam import IamDataFrame
from pyam.exceptions import format_log_message
from pyam.utils import make_index
from pydantic import model_validator

from scenariocompass.validation import GroupedValidator

logger = logging.getLogger(__name__)


class HistoricalVetting(GroupedValidator):
    prefix: str = "Historical Vetting"
    pattern: str = "historical_*.yaml"
    vetting_indicator: str = "Vetting|SCI 2025"

    @model_validator(mode="after")
    def set_criteria_names(self):
        for validator in self.validators:
            for item in validator.criteria_items:
                item.name = "|".join([self.prefix, item.variable[0], str(item.year[0])])
        return self

    def apply(self, df: IamDataFrame) -> IamDataFrame:

        df = self.reset_apply(df)

        # assume that all scenarios passed the vetting
        df.set_meta(name=self.vetting_indicator, meta="passed")

        # check that required variables exist
        required_variable_list = []
        for validator in self.validators:
            required_variable_list.extend(validator.input_data["variable"])
        missing_data = df.require_data(
            variable=required_variable_list,
            year=[2020, 2025],
        )
        if missing_data is not None:
            logger.warning(
                format_log_message(
                    "The following data are missing to do historical vetting",
                    missing_data,
                )
            )
            df.set_meta(
                name=self.vetting_indicator,
                meta="insufficient reporting",
                index=make_index(missing_data, ["model", "scenario"]),
            )

        # change error to warning and run validation
        # TODO consider custom log message for failing validation
        for validator in self.validators:
            # make copy of validator to not change error-level in actual instance
            _validator = validator.model_copy()
            for item in _validator.criteria_items:
                item.validation[0].warning_level = WarningEnum(40)
            df = _validator.apply(df)

        # assign aggregate meta-indicator from all validation criteria items
        for col in df.meta.columns:
            if col.startswith(self.prefix):
                df.meta[col] = df.meta[col].replace({"high": "failed"})

        vetting_result = df.meta[
            [col for col in df.meta.columns if col.startswith(self.prefix)]
        ]

        failed_vetting = vetting_result.apply(
            lambda x: any([i == "failed" for i in x]), axis=1
        )
        df.set_meta(
            name=self.vetting_indicator,
            meta="failed",
            index=failed_vetting[failed_vetting].index,
        )

        return df

    def reset_apply(self, df: IamDataFrame) -> IamDataFrame:
        df = super().reset_apply(df)

        if self.vetting_indicator in df.meta.columns:
            logger.info(f"Resetting '{self.vetting_indicator}' meta-indicator")
            df.meta.drop(self.vetting_indicator, axis=1, inplace=True)

        return df
