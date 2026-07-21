import logging
import sys
from pathlib import Path

import yaml
from nomenclature.processor import Processor
from pyam import IamDataFrame

from scenariocompass.emissions_diagnostics import EmissionsDiagnostics
from scenariocompass.flagging import FeasibilityValidator, SustainabilityValidator
from scenariocompass.historical_vetting import HistoricalVetting

here = Path(__file__).parent

try:
    __IPYTHON__  # type: ignore
    _in_ipython_session = True
except NameError:
    _in_ipython_session = False

_sys_has_ps1 = hasattr(sys, "ps1")

# Logging is only configured by default when used in an interactive environment.
# This follows the setup in ixmp4, pyam and nomenclature.
if _in_ipython_session or _sys_has_ps1:
    with open(here / "logging.yaml") as file:
        logging.config.dictConfig(yaml.safe_load(file))


class ScenarioCompassProcessor(Processor):
    """Run the diagnostics and validation for the Scenario Compass Initiative"""

    emissions_diagnostics: EmissionsDiagnostics = EmissionsDiagnostics()
    historical_vetting: HistoricalVetting = HistoricalVetting()
    feasibility_validator: FeasibilityValidator = FeasibilityValidator()
    sustainability_validator: SustainabilityValidator = SustainabilityValidator()

    def apply(self, df: IamDataFrame) -> IamDataFrame:

        for processor in [
            self.emissions_diagnostics,
            self.historical_vetting,
            self.feasibility_validator,
            self.sustainability_validator,
        ]:
            df = processor.apply(df)

        return df
