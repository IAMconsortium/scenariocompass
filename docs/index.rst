.. currentmodule:: scenariocompass

Evaluation & analysis for the Scenario Compass Initiative
=========================================================

Release v\ |version|

|license| |python| |ruff| |pytest| |rtd|

.. |license| image:: https://img.shields.io/badge/License-MIT-blue
   :target: https://github.com/IAMconsortium/scenariocompass/blob/main/LICENSE

.. |python| image:: https://img.shields.io/badge/python-≥3.11,<3.15-blue?logo=python&logoColor=white
   :target: https://github.com/IAMconsortium/scenariocompass

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff

.. |pytest| image:: https://img.shields.io/github/actions/workflow/status/IAMconsortium/scenariocompass/pytest.yml?logo=GitHub&label=pytest
   :target: https://github.com/IAMconsortium/scenariocompass/actions/workflows/pytest.yml

.. |rtd| image:: https://readthedocs.org/projects/scenariocompass/badge
   :target: https://scenariocompass.readthedocs.io

Overview
--------

The **scenariocompass** package provides utility functions for evaluation and analysis
of integrated-assessment and emissions scenarios as used by the Scenario Compass Initiative.
Visit https://scenariocompass.org for more information.

Scenario evaluation
~~~~~~~~~~~~~~~~~~~

The Scenario Compass Initiative develops criteria for scenario evaluation, specifically
validation of key variables against historical reference data and flagging of scenarios
if they violate feasibility and sustainability thresholds.

This package implements the scenario-evaluation criteria as specified in
**Release 2026-08-03** (August 3, 2026).
Visit https://scenario-evaluation-criteria.iamconsortium.org/2026.08.03/ for more
information and detailed explanation for the selected thresholds and ranges.

The current package implementation is consistent with **Release v1.1** of the
Scenario Compass ensemble (doi: `10.5281/zenodo.21805011`_) released on August 5, 2026.
The criteria are defined in the `scenariocompass/criteria`_ folder of the repository.

Climate categorization
~~~~~~~~~~~~~~~~~~~~~~

The Scenario Compass Initiative developed a new set of climate categories, incorporating
insights from IPCC AR6 WG3 and recent publications. Refer to the supplementary material
of `Riahi et al. (in review)`_ for more information.

Usage
-----

To use the **scenariocompass** package, you can use the following code, where `df`
is a |pyam.IamDataFrame| following the `common-definitions`_ variable template.

.. code-block:: python

    from scenariocompass import ScenarioCompassProcessor, ClimateCategorization

    # run the scenario evaluation on the scenario data
    sci_processor = ScenarioCompassProcessor()
    df = sci_processor.apply(df)

    # assign the SCI climate categorization
    sci_categories = ClimateCategorization()
    df = sci_categories.apply(df)

Refer to the :ref:`api` for more information.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   api
   tools

Acknowledgement & License
-------------------------

.. figure:: _static/iamc-logo.png
   :width: 160px
   :align: right

This package and related tools build on the work by the
`Integrated Assessment Modeling Consortium (IAMC) <https://www.iamconsortium.org>`_.

The Scenario Compass Initiative is grateful for the generous support from the
`Bezos Earth Fund <https://www.bezosearthfund.org>`_.

This package is developed and maintained by the |ScSe team|. It is released under the
`MIT License`_.

.. _`scenariocompass/criteria` : https://github.com/IAMconsortium/scenariocompass/tree/main/scenariocompass/criteria

.. _`10.5281/zenodo.21805011` : https://doi.org/10.5281/zenodo.21805011

.. _`Riahi et al. (in review)` : https://doi.org/10.21203/rs.3.rs-8891091/v1

.. _`pyam.IamDataFrame`: https://pyam-iamc.readthedocs.io

.. _`common-definitions` : https://github.com/IAMconsortium/common-definitions

.. _`MIT License` : https://github.com/IAMconsortium/scenariocompass/blob/main/LICENSE