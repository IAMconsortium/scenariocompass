from pathlib import Path

import pandas as pd
import pytest
from pyam import IamDataFrame

TEST_DATA_DIR = Path(__file__).parent.absolute() / "data"


EXP_CLIMATE_META = pd.read_csv(
    TEST_DATA_DIR / "climate-categorization-exp-meta.csv"
).set_index(["model", "scenario"])


@pytest.fixture(scope="function")
def emissions_df():
    return IamDataFrame(TEST_DATA_DIR / "emission-diagnostics-data.csv")


@pytest.fixture(scope="function")
def climate_df():
    yield IamDataFrame(TEST_DATA_DIR / "climate-categorization-test-data.csv")


@pytest.fixture(scope="function")
def historical_vetting_df():
    return IamDataFrame(TEST_DATA_DIR / "historical-vetting-data.csv")
