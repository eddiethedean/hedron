"""Curated optional extras and analysis workbenches for Hedron."""

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
from hedron_extras.specialty import DeviceBridge, Joystick, TerminalPolicy, TerminalView
from hedron_extras.workbench import (
    CallableActionForm,
    ChartWorkbench,
    CodeEditor,
    DataExplorer,
    JSONEditor,
)

__version__ = "0.23.0"

__all__ = [
    "AvatarProfile",
    "BadgeLink",
    "BrowserPythonSandbox",
    "Calendar",
    "CallableActionForm",
    "ChartWorkbench",
    "ChoiceCards",
    "ChoiceOption",
    "CodeEditor",
    "DataExplorer",
    "DeviceBridge",
    "DiagramOutput",
    "FloatingAction",
    "FocusScrollRequest",
    "ImageAnnotations",
    "ImageCompare",
    "ImageCrop",
    "ImageRegionSelect",
    "JSONEditor",
    "Joystick",
    "KeyboardShortcuts",
    "LogConsole",
    "MetricCard",
    "SandboxBudget",
    "ShortcutBinding",
    "SignaturePad",
    "SplitPane",
    "Steps",
    "TerminalPolicy",
    "TerminalView",
    "TodoList",
    "TokenWeightedText",
    "TreeNodeProps",
    "TreeView",
    "Typeahead",
    "__version__",
]
