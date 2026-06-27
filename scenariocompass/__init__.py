import logging
import sys
from pathlib import Path

import yaml

from .emissions_diagnostics import EmissionsDiagnostics  # noqa
from .historical_vetting import HistoricalVetting  # noqa

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
