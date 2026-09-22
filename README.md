# Evaluation & analysis for the Scenario Compass Initiative

[![license](https://img.shields.io/badge/License-MIT-blue)](https://github.com/IAMconsortium/scenariocompass/blob/main/LICENSE)
[![python](https://img.shields.io/badge/python-≥3.11,<3.15-blue?logo=python&logoColor=white)](https://github.com/IAMconsortium/scenariocompass)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pytest](https://img.shields.io/github/actions/workflow/status/IAMconsortium/scenariocompass/pytest.yml?logo=GitHub&label=pytest)](https://github.com/IAMconsortium/scenariocompass/actions/workflows/pytest.yml)
[![rtd](https://readthedocs.org/projects/scenariocompass/badge)](https://scenariocompass.readthedocs.io)

Copyright 2026 IIASA and the Scenario Compass Initiative (SCI)

This repository is licensed under the [MIT License](LICENSE).

## Overview

<a href="https://scenariocompass.org">
<img src="./docs/_static/SCI-logo-title.svg" width="400" align="right" alt="Scenario Compass Initiative logo" />
</a>

This package provides utility functions for validation and analysis of Integrated-Assessment scenarios
as used by the Scenario Compass Initiative.

Visit https://scenariocompass.org for more information.

### Scenario evaluation

The Scenario Compass Initiative develops criteria for scenario evaluation, specifically
validation of key variables against historical reference data.

This package implements the scenario-evaluation criteria as specified
in **Release 2026-08-03** (August 3, 2026).
Visit https://scenario-evaluation-criteria.iamconsortium.org/2026.08.03/ for more information
and detailed explanation for the selected thresholds and ranges.

The current package is consistent with **Release v1.1** of the Scenario Compass ensemble
(doi [10.5281/zenodo.21805011](https://doi.org/10.5281/zenodo.21805011)) released on August 5, 2026.
The criteria are given in the directory [scenariocompass/criteria](scenariocompass/criteria)
and the package source code.

### Climate categorization

The Scenario Compass Initiative developed a new set of climate categories, incorporating
insights from IPCC AR6 WG3 and recent publications. Refer to the supplementary material
of [Riahi et al. (in review)](https://doi.org/10.21203/rs.3.rs-8891091/v1) for more information.

## Using the package

To use the **scenariocompass** package, you can use the following code, where `df`
is a **pyam.IamDataFrame** following the
[common-definitions](https://github.com/IAMconsortium/common-definitions) variable template.

```python
from scenariocompass import ScenarioCompassProcessor, ClimateCategorization

# run the scenario evaluation on the scenario data
sci_processor = ScenarioCompassProcessor()
df = sci_processor.apply(df)

# assign the SCI climate categorization
sci_categories = ClimateCategorization()
df = sci_categories.apply(df)
```

Refer to the [documentation](https://scenariocompass.readthedocs.io) for more information.

## Acknowledgement

<img src="./docs/_static/iamc-logo.png" width="200" align="right" alt="IAMC logo" />

This package and related tools build on the work by the <br />
[Integrated Assessment Modeling Consortium (IAMC)](https://www.iamconsortium.org).

The Scenario Compass Initiative is grateful for the generous support from the 
[Bezos Earth Fund](https://www.bezosearthfund.org).

This package is developed and maintained by the [Scenario Services team](https://software.ece,iiasa.ac.at)
at the IIASA Energy, Climate, and Environment program. It is released under the [MIT License](LICENSE).

