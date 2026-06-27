import logging
from pathlib import Path

from nomenclature.processor import Processor, DataValidator
from nomenclature.processor.data_validator import WarningEnum
from pyam import IamDataFrame
from sqlalchemy.sql.annotation import Annotated

here = Path(__file__).absolute().parent
criteria_dir = here.parent / "criteria" / "validate_data"


logger = logging.getLogger(__name__)


class HistoricalVetting(Processor):
    prefix : str = "Historical Vetting"
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
                item.name = "|".join(
                    [self.prefix, item.variable[0], str(item.year[0])]
                )

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

        # use `exclude` attribute to track missing data
        previous_exclude = df.exclude.copy()
        df.exclude = False

        # change error to warning
        for validator in self.validators:
            _validator = validator.model_copy()
            for item in _validator.criteria_items:
                df.require_data(**item.filter_args, exclude_on_fail=True)
                item.validation[0].warning_level = WarningEnum(40)

            df = _validator.apply(df)

        df.set_meta(name="Vetting|SCI 2025", meta="passed")
        df.set_meta(
            name="Vetting|SCI 2025",
            meta="insufficient reporting",
            index=df.filter(exclude=True).index,
        )
        for col in df.meta.columns:
            if col.startswith("Historical Vetting"):
                df.meta[col] = df.meta[col].replace({"high": "failed"})

        df.exclude = previous_exclude

        return df

    def reset_apply(self, df: IamDataFrame) -> IamDataFrame:
        self._update_names()
        criteria_cols = [col for col in df.meta.columns if col.startswith(self.prefix)]
        if criteria_cols:
            logger.info(f"Resetting {len(criteria_cols)} historical vetting criteria")
            df.meta.drop(criteria_cols, axis=1, inplace=True)
        else:
            logger.info(f"No historical vetting criteria to reset")

        return df
