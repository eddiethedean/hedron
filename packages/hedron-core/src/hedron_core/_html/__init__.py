"""Private HTML attribute policy shared by constructors and the serializer."""

from hedron_core._html.policy import (
    HtmlAttributePolicy,
    default_html_policy,
    is_safe_layout_style,
    normalize_attrs,
    normalize_srcset,
    require_safe_attr_name,
)

__all__ = [
    "HtmlAttributePolicy",
    "default_html_policy",
    "is_safe_layout_style",
    "normalize_attrs",
    "normalize_srcset",
    "require_safe_attr_name",
]
