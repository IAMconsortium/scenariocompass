from pathlib import Path

import pytest
from pyam import IamDataFrame

TEST_DATA_DIR = Path(__file__).parent.absolute() / "data"

@pytest.fixture(scope="function")
def emissions_df():
    yield IamDataFrame(TEST_DATA_DIR / "emission_diagnostics.csv")


@pytest.fixture(scope="function")
def climate_df():
    yield IamDataFrame(TEST_DATA_DIR / "climate-categorization-test-data.csv")
