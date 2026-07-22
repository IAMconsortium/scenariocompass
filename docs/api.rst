API Reference
=============

.. currentmodule:: scenariocompass

Processors
----------

.. autoclass:: ScenarioCompassProcessor
   :members: historical_vetting, feasibility_validator, sustainability_validator, apply

.. autoclass:: EmissionsDiagnostics
   :members: input_data, output_meta, apply

.. autoclass:: HistoricalVetting
   :members: prefix, vetting_indicator, validators, apply, criteria_names, reset_apply

.. autoclass:: FeasibilityValidator
   :members: pattern, validators, apply, criteria_names, reset_apply

.. autoclass:: SustainabilityValidator
   :members: pattern, validators, apply, criteria_names, reset_apply