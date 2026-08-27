"""Edron: a class-oriented authoring facade for Hedron."""

__version__ = "0.6.0"

from edron.app import App
from edron.cache import CachedFunction, cache_data
from edron.capabilities import (
    BrokenCapabilityError,
    CapabilityError,
    IncompatibleCapabilityError,
    MissingCapabilityError,
)
from edron.composition import FeaturePackage, PackageConflictError, feature_package
from edron.confirm import Confirm
from edron.data import (
    AuditEvent,
    CellEdit,
    Column,
    DataExport,
    DataSelection,
    DataSource,
    DataWorkspace,
    EditIntent,
    EditPolicy,
    PageRequest,
    WorkspacePage,
)
from edron.dependencies import Dependency, Resource, dependency, resource
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
from edron.jobs import (  # pyright: ignore[reportUnknownVariableType]
    JobBackend,
    JobFlow,
    JobScope,
    job_status_events,
)
from edron.navigation import LAYOUT_KINDS, LayoutSpec, NavigationError, NavigationTarget, layout
from edron.outcomes import Outcome, refresh, success
from edron.page import Container, FilterScope, Page
from edron.promotion import CapabilityPromotion, promoted_capabilities, promoted_capability
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
    "CapabilityPromotion",
    "Color",
    "Column",
    "Confirm",
    "Container",
    "Dependency",
    "Resource",
    "DataExport",
    "DataSelection",
    "DataSource",
    "DataWorkspace",
    "DiagnosticReport",
    "DesignSystem",
    "Download",
    "EdronError",
    "EdronDiagnostic",
    "EditIntent",
    "EditPolicy",
    "FilterScope",
    "FeaturePackage",
    "Fragment",
    "IncompatibleCapabilityError",
    "JobBackend",
    "JobFlow",
    "JobScope",
    "job_status_events",
    "MissingCapabilityError",
    "BrokenCapabilityError",
    "Outcome",
    "PackageConflictError",
    "Page",
    "PageRequest",
    "LayoutSpec",
    "NavigationError",
    "NavigationTarget",
    "LAYOUT_KINDS",
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
    "resource",
    "download",
    "fragment",
    "inherit",
    "expose",
    "refresh",
    "success",
    "theme",
    "feature_package",
    "layout",
    "promoted_capability",
    "promoted_capabilities",
    "SourceLocation",
    "WorkspacePage",
    "AuditEvent",
    "CellEdit",
]
