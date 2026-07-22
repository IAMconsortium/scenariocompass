from nomenclature.processor import Processor
from pyam import IamDataFrame

from scenariocompass.emissions_diagnostics import EmissionsDiagnostics
from scenariocompass.flagging import FeasibilityValidator, SustainabilityValidator
from scenariocompass.historical_vetting import HistoricalVetting


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
