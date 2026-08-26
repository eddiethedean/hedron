"""Edron: a class-oriented authoring facade for Hedron."""

__version__ = "0.2.0"

from edron.app import App
from edron.cache import CachedFunction, cache_data
from edron.capabilities import (
    BrokenCapabilityError,
    CapabilityError,
    IncompatibleCapabilityError,
    MissingCapabilityError,
)
from edron.confirm import Confirm
from edron.dependencies import Dependency, dependency
from edron.descriptors import (
    Action,
    BoundAction,
    BoundFragment,
    Fragment,
    action,
    expose,
    fragment,
    inherit,
)
from edron.diagnostics import DiagnosticReport, EdronDiagnostic, SourceLocation
from edron.downloads import Download, download
from edron.errors import BindingError, EdronError, PhaseError, RegistrationError
from edron.jobs import JobBackend, JobFlow, JobScope  # pyright: ignore[reportUnknownVariableType]
from edron.outcomes import Outcome, refresh, success
from edron.page import Container, FilterScope, Page
from edron.scaffolds import TEMPLATES, create_scaffold
from edron.styling import Color, DesignSystem, StyleContext, StyleRecipe, Theme, ThemeSpec, theme

__all__ = [
    "Action",
    "App",
    "BindingError",
    "BoundAction",
    "BoundFragment",
    "CachedFunction",
    "CapabilityError",
    "Color",
    "Confirm",
    "Container",
    "Dependency",
    "DiagnosticReport",
    "DesignSystem",
    "Download",
    "EdronError",
    "EdronDiagnostic",
    "FilterScope",
    "Fragment",
    "IncompatibleCapabilityError",
    "JobBackend",
    "JobFlow",
    "JobScope",
    "MissingCapabilityError",
    "BrokenCapabilityError",
    "Outcome",
    "Page",
    "PhaseError",
    "RegistrationError",
    "StyleContext",
    "StyleRecipe",
    "Theme",
    "ThemeSpec",
    "TEMPLATES",
    "action",
    "cache_data",
    "create_scaffold",
    "dependency",
    "download",
    "fragment",
    "inherit",
    "expose",
    "refresh",
    "success",
    "theme",
    "SourceLocation",
]
