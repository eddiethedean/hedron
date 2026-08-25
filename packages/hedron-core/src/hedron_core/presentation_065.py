"""Phase 0.65 styling contracts.

The implementation remains source-compatible with the 0.64 presentation
module while giving integrations a phase-specific import path.
"""

from hedron_core.presentation_064 import (
    PRESENTATION_SCHEMA,
    PRESENTATION_TOKEN_MANIFEST,
    MotionRecipe,
    PresentationContract,
    PresentationError,
    ResponsiveCondition,
    ScopedStyleBundle,
    ScopedStyleRecipe,
    application_style_hook_data,
    application_style_hook_manifest,
    compile_scoped_styles,
    component_presentation_manifest,
    motion_recipe,
    motion_recipes,
    presentation_contract,
    presentation_token_manifest,
    presentation_tokens,
)

__all__ = [
    "PRESENTATION_SCHEMA",
    "PRESENTATION_TOKEN_MANIFEST",
    "MotionRecipe",
    "PresentationContract",
    "PresentationError",
    "ResponsiveCondition",
    "ScopedStyleBundle",
    "ScopedStyleRecipe",
    "application_style_hook_data",
    "application_style_hook_manifest",
    "compile_scoped_styles",
    "component_presentation_manifest",
    "presentation_contract",
    "presentation_token_manifest",
    "presentation_tokens",
    "motion_recipe",
    "motion_recipes",
]
