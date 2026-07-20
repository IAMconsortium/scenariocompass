from pathlib import Path

from nomenclature.processor import DataValidator

here = Path(__file__).absolute().parent
criteria_dir = here.parent / "criteria" / "validate_data"


def parse_validators(values, default_pattern):
    if not values.get("validators", False):
        values["validators"] = [
            DataValidator.from_file(file)
            for file in criteria_dir.glob(values.get("pattern", default_pattern))
        ]
    return values
