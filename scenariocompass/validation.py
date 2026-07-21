import logging
from pathlib import Path

from nomenclature.processor import Processor, DataValidator
from pyam import IamDataFrame
from pydantic import model_validator


logger = logging.getLogger(__name__)


here = Path(__file__).absolute().parent
criteria_dir = here.parent / "criteria" / "validate_data"


class GroupedValidator(Processor):
    pattern: str
    prefix: str
    validators: list[DataValidator] = []

    @model_validator(mode="before")
    @classmethod
    def parse_validators(cls, values):
        if not values.get("validators", False):
            values["validators"] = [
                DataValidator.from_file(file)
                for file in criteria_dir.glob(
                    values.get("pattern", cls.model_fields["pattern"].default)
                )
            ]
        return values

    @property
    def criteria_names(self) -> list[str]:
        """Get the names of criteria"""
        return [
            item.name
            for validator in self.validators
            for item in validator.criteria_items
            if item.name is not None
        ]

    def apply(self, df: IamDataFrame) -> IamDataFrame:
        """Apply the criteria to the IamDataFrame"""
        for validator in self.validators:
            validator.apply(df)
        return df

    def reset_apply(self, df: IamDataFrame) -> IamDataFrame:
        """Remove all meta indicators starting with the processor-prefix"""
        flagging_cols = [col for col in df.meta.columns if col.startswith(self.prefix)]

        if flagging_cols:
            logger.info(f"Resetting {len(flagging_cols)} criteria")
            df.meta.drop(flagging_cols, axis=1, inplace=True)

        return df
