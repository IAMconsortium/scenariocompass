API Reference
=============

.. currentmodule:: scenariocompass

Processors
----------

.. autoclass:: EmissionsDiagnostics
   :members: input_data, output_meta, apply

.. autofunction:: scenariocompass.emissions_diagnostics.compute_cumulative_eoc

.. autofunction:: scenariocompass.emissions_diagnostics.year_of_netzero

.. autoclass:: HistoricalVetting
   :members: prefix, vetting_indicator, validators, apply, criteria_names, reset_apply
