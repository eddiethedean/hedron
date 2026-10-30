"""Optional pytest/Playwright scenarios for real Hedron pages.

This beta surface is loaded explicitly through
``hedron.testing.pytest_plugin``. Imports of this module do not import pytest,
Playwright, or Uvicorn; managed hosting imports Uvicorn only in the spawned
application process.
"""

from __future__ import annotations

from hedron.testing._ui_testing.contribution import (
    UITestingContribution as UITestingContribution,
)
from hedron.testing._ui_testing.contribution import (
    validate_ui_testing_contribution as validate_ui_testing_contribution,
)
from hedron.testing._ui_testing.host import (
    ManagedHostCleanupError as ManagedHostCleanupError,
)
from hedron.testing._ui_testing.host import ManagedHostError as ManagedHostError
from hedron.testing._ui_testing.scenario import (
    AmbiguousSettleError as AmbiguousSettleError,
)
from hedron.testing._ui_testing.scenario import (
    BrowserScenario as BrowserScenario,
)
from hedron.testing._ui_testing.scenario import (
    BrowserScenarioFactory as BrowserScenarioFactory,
)
from hedron.testing._ui_testing.scenario import (
    Checkpoint as Checkpoint,
)
from hedron.testing._ui_testing.scenario import (
    CleanCheckError as CleanCheckError,
)
from hedron.testing._ui_testing.scenario import (
    InvalidCheckpointError as InvalidCheckpointError,
)
from hedron.testing._ui_testing.scenario import (
    ObservationUnavailableError as ObservationUnavailableError,
)
from hedron.testing._ui_testing.scenario import (
    SettleResult as SettleResult,
)
from hedron.testing._ui_testing.scenario import (
    SettleTimeoutError as SettleTimeoutError,
)
from hedron.testing._ui_testing.scenario import (
    UIConfigurationError as UIConfigurationError,
)
from hedron.testing._ui_testing.scenario import UIEvent as UIEvent
from hedron.testing._ui_testing.scenario import UIHarnessError as UIHarnessError

__all__ = [
    "BrowserScenario",
    "BrowserScenarioFactory",
    "AmbiguousSettleError",
    "Checkpoint",
    "CleanCheckError",
    "InvalidCheckpointError",
    "ManagedHostCleanupError",
    "ManagedHostError",
    "ObservationUnavailableError",
    "SettleResult",
    "SettleTimeoutError",
    "UIConfigurationError",
    "UIEvent",
    "UIHarnessError",
    "UITestingContribution",
    "validate_ui_testing_contribution",
]
