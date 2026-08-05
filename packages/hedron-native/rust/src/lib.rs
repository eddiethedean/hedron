//! Bulk HTML escaping for Hedron (batch FFI; never per-node tree walking).

use pyo3::prelude::*;

fn escape_text_inner(value: &str) -> String {
    let mut out = String::with_capacity(value.len());
    for ch in value.chars() {
        if ch == '\0' {
            continue;
        }
        match ch {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            _ => out.push(ch),
        }
    }
    out
}

fn escape_attr_inner(value: &str) -> String {
    let mut out = String::with_capacity(value.len());
    for ch in value.chars() {
        if ch == '\0' {
            continue;
        }
        match ch {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            '\'' => out.push_str("&#x27;"),
            _ => out.push(ch),
        }
    }
    out
}

#[pymodule]
mod _native {
    use pyo3::prelude::*;
    use super::{escape_attr_inner, escape_text_inner};

    #[pyfunction]
    fn escape_text(value: &str) -> String {
        escape_text_inner(value)
    }

    #[pyfunction]
    fn escape_attr(value: &str) -> String {
        escape_attr_inner(value)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn escapes_text() {
        assert_eq!(escape_text_inner("<script>&"), "&lt;script&gt;&amp;");
        assert_eq!(escape_text_inner("a\0b"), "ab");
    }

    #[test]
    fn escapes_attr() {
        assert_eq!(escape_attr_inner("a\"b'c"), "a&quot;b&#x27;c");
    }
}
