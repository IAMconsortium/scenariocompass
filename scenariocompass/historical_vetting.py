import logging
from pathlib import Path

from nomenclature.processor import Processor, DataValidator
from nomenclature.processor.data_validator import WarningEnum
from pyam import IamDataFrame
from pyam.exceptions import format_log_message
from pyam.utils import make_index

here = Path(__file__).absolute().parent
criteria_dir = here.parent / "criteria" / "validate_data"


logger = logging.getLogger(__name__)


class HistoricalVetting(Processor):
    prefix: str = "Historical Vetting"
    vetting_indicator = "Vetting|SCI 2025"
    validators: list[DataValidator] = [
        DataValidator.from_file(criteria_dir / "historical_emissions.yaml"),
        DataValidator.from_file(criteria_dir / "historical_energy_balances.yaml"),
    ]

    @property
    def input_data(self):
        return list()

    def _update_names(self):
        """Reset validator-item-names to "Historical Vetting|<Variable>|<Year>" """
        for validator in self.validators:
            for item in validator.criteria_items:
                item.name = "|".join([self.prefix, item.variable[0], str(item.year[0])])

    @property
    def criteria_names(self):
        """Get the names of historical vetting criteria"""
        self._update_names()
        names = list()
        for validator in self.validators:
            for item in validator.criteria_items:
                names.append(item.name)
        return names

    def apply(self, df: IamDataFrame) -> IamDataFrame:
        self._update_names()
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
        self._update_names()
        criteria_cols = [col for col in df.meta.columns if col.startswith(self.prefix)]
        if criteria_cols:
            logger.info(f"Resetting {len(criteria_cols)} historical vetting criteria")
            df.meta.drop(criteria_cols, axis=1, inplace=True)
        else:
            logger.info("No historical vetting criteria to reset")

        return df
