from scenariocompass import (
    HistoricalVetting,
    FeasibilityValidator,
    SustainabilityValidator,
)
from scenariocompass.flagging import META_CCS_CONCERN_NAME


def test_historical_vetting():
    """Check that historical vetting is imported as expected."""
    historical_vetting = HistoricalVetting()

    assert (
        "Historical Vetting|Emissions|CO2|Energy and Industrial Processes|2010"
        in historical_vetting.criteria_names
    )


def test_feasibility_validator():
    """Check that feasibility validation is imported as expected."""
    validator = FeasibilityValidator()
    assert "Feasibility Concern|Carbon Capture|World|2030" in validator.criteria_names


def test_sustainability_validator():
    """Check that sustainability validation is imported as expected."""
    validator = SustainabilityValidator()
    assert (
        "Sustainability Concern|Unsustainable Bioenergy Use|World"
        in validator.criteria_names
    )
    # check that the manual addition of the cumulative-CCS-concern works
    assert META_CCS_CONCERN_NAME in validator.criteria_names
