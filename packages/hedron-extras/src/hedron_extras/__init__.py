"""Curated optional extras and analysis workbenches for Hedron.

EXTRAS-025 landmines (CodeEditor, TerminalView, Joystick, DeviceBridge) are not
exported here — import from ``hedron_extras.experimental`` and install
``hedron[experimental-ui]``.
"""

from __future__ import annotations

from hedron_extras.composition import (
    ChoiceCards,
    ChoiceOption,
    FloatingAction,
    FocusScrollRequest,
    KeyboardShortcuts,
    ShortcutBinding,
    SplitPane,
    Steps,
    TreeNodeProps,
    TreeView,
)
from hedron_extras.display import DiagramOutput, LogConsole, TokenWeightedText
from hedron_extras.editors import Calendar, SignaturePad, Typeahead
from hedron_extras.image_tools import ImageAnnotations, ImageCompare, ImageCrop, ImageRegionSelect
from hedron_extras.recipes import AvatarProfile, BadgeLink, MetricCard, TodoList
from hedron_extras.sandbox import BrowserPythonSandbox, SandboxBudget
from hedron_extras.workbench import (
    CallableActionForm,
    ChartWorkbench,
    DataExplorer,
    JSONEditor,
)

__version__ = "0.40.0"

__all__ = [
    "AvatarProfile",
    "BadgeLink",
    "BrowserPythonSandbox",
    "Calendar",
    "CallableActionForm",
    "ChartWorkbench",
    "ChoiceCards",
    "ChoiceOption",
    "DataExplorer",
    "DiagramOutput",
    "FloatingAction",
    "FocusScrollRequest",
    "ImageAnnotations",
    "ImageCompare",
    "ImageCrop",
    "ImageRegionSelect",
    "JSONEditor",
    "KeyboardShortcuts",
    "LogConsole",
    "MetricCard",
    "SandboxBudget",
    "ShortcutBinding",
    "SignaturePad",
    "SplitPane",
    "Steps",
    "TodoList",
    "TokenWeightedText",
    "TreeNodeProps",
    "TreeView",
    "Typeahead",
    "__version__",
]
