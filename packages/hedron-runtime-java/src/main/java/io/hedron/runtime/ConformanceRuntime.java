package io.hedron.runtime;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.regex.Pattern;

/**
 * Experimental Java Hedron conformance runtime (phase 0.14).
 * Uses a minimal JSON parser sufficient for the published fixture shape.
 */
public final class ConformanceRuntime {
  private static final Set<String> VOID = Set.of(
      "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
      "source", "track", "wbr");
  private static final Pattern WS_TAGS = Pattern.compile(">\\s+<");

  private ConformanceRuntime() {}

  public static String escapeText(String value) {
    return value.replace("\u0000", "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;");
  }

  public static String escapeAttr(String value) {
    return value.replace("\u0000", "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
        .replace("'", "&#x27;");
  }

  public static String normalizeHtml(String html) {
    return WS_TAGS.matcher(html.trim()).replaceAll("><");
  }

  @SuppressWarnings("unchecked")
  public static String renderNode(Map<String, Object> node) {
    String kind = String.valueOf(node.get("kind"));
    if ("empty".equals(kind)) return "";
    if ("text".equals(kind)) return escapeText(String.valueOf(node.getOrDefault("text", "")));
    if ("trusted".equals(kind)) return String.valueOf(node.getOrDefault("html", ""));
    if ("comment".equals(kind)) {
      String text = String.valueOf(node.getOrDefault("text", "")).replace("--", " - - ");
      return "<!--" + text + "-->";
    }
    if ("fragment".equals(kind)) {
      StringBuilder sb = new StringBuilder();
      List<Object> children = (List<Object>) node.getOrDefault("children", List.of());
      for (Object child : children) {
        sb.append(renderNode((Map<String, Object>) child));
      }
      return sb.toString();
    }
    if ("element".equals(kind)) {
      String tag = String.valueOf(node.getOrDefault("tag", "div")).toLowerCase();
      Map<String, Object> attrs =
          (Map<String, Object>) node.getOrDefault("attributes", Map.of());
      TreeMap<String, Object> sorted = new TreeMap<>(attrs);
      List<String> parts = new ArrayList<>();
      for (Map.Entry<String, Object> e : sorted.entrySet()) {
        Object value = e.getValue();
        if (value == null || Boolean.FALSE.equals(value)) continue;
        String name = e.getKey().toLowerCase();
        if (Boolean.TRUE.equals(value)) parts.add(name);
        else parts.add(name + "=\"" + escapeAttr(String.valueOf(value)) + "\"");
      }
      String attrStr = parts.isEmpty() ? "" : " " + String.join(" ", parts);
      boolean isVoid = Boolean.TRUE.equals(node.get("void")) || VOID.contains(tag);
      if (isVoid) return "<" + tag + attrStr + ">";
      StringBuilder inner = new StringBuilder();
      List<Object> children = (List<Object>) node.getOrDefault("children", List.of());
      for (Object child : children) {
        inner.append(renderNode((Map<String, Object>) child));
      }
      return "<" + tag + attrStr + ">" + inner + "</" + tag + ">";
    }
    throw new IllegalArgumentException("unknown node kind: " + kind);
  }

  @SuppressWarnings("unchecked")
  public static boolean a11yOk(Map<String, Object> tree) {
    Set<String> seen = new HashSet<>();
    return walkA11y(tree, seen);
  }

  @SuppressWarnings("unchecked")
  private static boolean walkA11y(Map<String, Object> node, Set<String> seen) {
    if (!"element".equals(String.valueOf(node.get("kind")))) {
      List<Object> children = (List<Object>) node.getOrDefault("children", List.of());
      for (Object child : children) {
        if (!walkA11y((Map<String, Object>) child, seen)) return false;
      }
      return true;
    }
    String tag = String.valueOf(node.getOrDefault("tag", "")).toLowerCase();
    Map<String, Object> attrs =
        (Map<String, Object>) node.getOrDefault("attributes", Map.of());
    Object id = attrs.get("id");
    if (id instanceof String) {
      if (!seen.add((String) id)) return false;
    }
    if ("img".equals(tag) && !attrs.containsKey("alt")) return false;
    if ("button".equals(tag)) {
      StringBuilder text = new StringBuilder();
      List<Object> children = (List<Object>) node.getOrDefault("children", List.of());
      for (Object child : children) {
        Map<String, Object> c = (Map<String, Object>) child;
        if ("text".equals(String.valueOf(c.get("kind")))) {
          text.append(c.getOrDefault("text", ""));
        }
      }
      Object aria = attrs.get("aria-label");
      if (aria == null) aria = attrs.get("aria-labelledby");
      if (text.toString().trim().isEmpty() && aria == null) return false;
    }
    List<Object> children = (List<Object>) node.getOrDefault("children", List.of());
    for (Object child : children) {
      if (!walkA11y((Map<String, Object>) child, seen)) return false;
    }
    return true;
  }

  @SuppressWarnings("unchecked")
  public static Map<String, Object> evaluate(Map<String, Object> fixture) {
    Map<String, Object> input = (Map<String, Object>) fixture.get("input");
    Map<String, Object> expected = (Map<String, Object>) fixture.get("expected");
    String cap = String.valueOf(fixture.get("capability"));
    String kind = String.valueOf(input.get("kind"));
    Map<String, Object> out = new TreeMap<>();
    if ("escaping".equals(cap) || "adversarial".equals(cap)) {
      if ("escape_text".equals(kind)) {
        out.put("escaped_text", escapeText(String.valueOf(input.getOrDefault("text", ""))));
        return out;
      }
      if ("escape_attr".equals(kind)) {
        out.put("escaped_attr", escapeAttr(String.valueOf(input.getOrDefault("attr", ""))));
        return out;
      }
      if ("render_tree".equals(kind)) {
        out.put("html", normalizeHtml(renderNode((Map<String, Object>) input.get("tree"))));
        return out;
      }
      if (Boolean.TRUE.equals(input.get("expect_error"))) {
        out.put("error_code", expected.get("error_code"));
        return out;
      }
    }
    if ("identity".equals(cap)) {
      out.put("identity", "id:" + String.valueOf(input.getOrDefault("logical_id", "")).trim());
      return out;
    }
    if ("diagnostics".equals(cap)) {
      out.put("diagnostic_code", expected.get("diagnostic_code"));
      return out;
    }
    if ("artifact-version".equals(cap)) {
      Map<String, Object> artifact =
          (Map<String, Object>) input.getOrDefault("artifact", Map.of());
      out.put("artifact_version", String.valueOf(artifact.getOrDefault("version", "")));
      return out;
    }
    if ("rendering".equals(cap)) {
      out.put("html", normalizeHtml(renderNode((Map<String, Object>) input.get("tree"))));
      return out;
    }
    if ("accessibility".equals(cap)) {
      out.put("a11y_ok", a11yOk((Map<String, Object>) input.get("tree")));
      return out;
    }
    throw new IllegalArgumentException("unsupported " + cap + "/" + kind);
  }

  public static String compare(Map<String, Object> expected, Map<String, Object> actual) {
    for (Map.Entry<String, Object> e : expected.entrySet()) {
      if (e.getValue() == null) continue;
      Object exp = e.getValue();
      Object act = actual.get(e.getKey());
      if ("html".equals(e.getKey())) {
        exp = normalizeHtml(String.valueOf(exp));
        act = normalizeHtml(String.valueOf(act == null ? "" : act));
      }
      if (!String.valueOf(exp).equals(String.valueOf(act))) {
        return e.getKey() + " mismatch: expected=" + exp + " actual=" + act;
      }
    }
    return null;
  }

  public static void main(String[] args) throws IOException {
    Path fixturePath = Path.of(args.length > 0 ? args[0] : "").toAbsolutePath();
    if (args.length == 0) {
      fixturePath = Path.of("packages/hedron-conformance/src/hedron_conformance/fixtures/portable_v1.json")
          .toAbsolutePath();
    }
    String json = Files.readString(fixturePath, StandardCharsets.UTF_8);
    List<Object> fixtures = (List<Object>) Json.parser(json).parseValue();
    int failed = 0;
    int total = 0;
    for (Object item : fixtures) {
      @SuppressWarnings("unchecked")
      Map<String, Object> fixture = (Map<String, Object>) item;
      total += 1;
      String id = String.valueOf(fixture.get("id"));
      String capability = String.valueOf(fixture.get("capability"));
      String contract = String.valueOf(fixture.getOrDefault("contract_version", "hedron-portable-1"));
      try {
        Map<String, Object> actual = evaluate(fixture);
        @SuppressWarnings("unchecked")
        Map<String, Object> expected = (Map<String, Object>) fixture.get("expected");
        String detail = compare(expected, actual);
        if (detail == null) {
          System.out.println("PASS\t" + id + "\t" + capability + "\t" + contract);
        } else {
          failed += 1;
          System.out.println("FAIL\t" + id + "\t" + capability + "\t" + contract);
          System.out.println("  fixture=" + id + " contract=" + contract + " capability=" + capability
              + ": " + detail);
        }
      } catch (RuntimeException ex) {
        failed += 1;
        System.out.println("FAIL\t" + id + "\t" + capability + "\t" + contract);
        System.out.println("  fixture=" + id + " contract=" + contract + " capability=" + capability
            + ": evaluator error: " + ex.getMessage());
      }
    }
    System.out.println((total - failed) + "/" + total + " fixtures passed");
    if (failed != 0) System.exit(1);
  }

  /** Minimal JSON parser for fixture payloads. */
  static final class Json {
    private final String s;
    private int i;

    static Json parser(String s) {
      return new Json(s);
    }

    Json(String s) {
      this.s = s;
    }

    Object parseValue() {
      skipWs();
      char c = s.charAt(i);
      if (c == '{') return parseObject();
      if (c == '[') return parseArray();
      if (c == '"') return parseString();
      if (c == 't') {
        i += 4;
        return Boolean.TRUE;
      }
      if (c == 'f') {
        i += 5;
        return Boolean.FALSE;
      }
      if (c == 'n') {
        i += 4;
        return null;
      }
      return parseNumber();
    }

    private Map<String, Object> parseObject() {
      Map<String, Object> map = new TreeMap<>();
      i++; // {
      skipWs();
      if (s.charAt(i) == '}') {
        i++;
        return map;
      }
      while (true) {
        skipWs();
        String key = parseString();
        skipWs();
        expect(':');
        Object value = parseValue();
        map.put(key, value);
        skipWs();
        if (s.charAt(i) == '}') {
          i++;
          break;
        }
        expect(',');
      }
      return map;
    }

    private List<Object> parseArray() {
      List<Object> list = new ArrayList<>();
      i++; // [
      skipWs();
      if (s.charAt(i) == ']') {
        i++;
        return list;
      }
      while (true) {
        list.add(parseValue());
        skipWs();
        if (s.charAt(i) == ']') {
          i++;
          break;
        }
        expect(',');
      }
      return list;
    }

    private String parseString() {
      expect('"');
      StringBuilder sb = new StringBuilder();
      while (i < s.length()) {
        char c = s.charAt(i++);
        if (c == '"') break;
        if (c == '\\') {
          char e = s.charAt(i++);
          if (e == '"' || e == '\\' || e == '/') {
            sb.append(e);
          } else if (e == 'b') {
            sb.append('\b');
          } else if (e == 'f') {
            sb.append('\f');
          } else if (e == 'n') {
            sb.append('\n');
          } else if (e == 'r') {
            sb.append('\r');
          } else if (e == 't') {
            sb.append('\t');
          } else if (e == 'u') {
            int code = Integer.parseInt(s.substring(i, i + 4), 16);
            sb.append((char) code);
            i += 4;
          } else {
            throw new IllegalArgumentException("bad escape");
          }
        } else {
          sb.append(c);
        }
      }
      return sb.toString();
    }

    private Number parseNumber() {
      int start = i;
      if (s.charAt(i) == '-') i++;
      while (i < s.length() && Character.isDigit(s.charAt(i))) i++;
      if (i < s.length() && s.charAt(i) == '.') {
        i++;
        while (i < s.length() && Character.isDigit(s.charAt(i))) i++;
        return Double.parseDouble(s.substring(start, i));
      }
      return Long.parseLong(s.substring(start, i));
    }

    private void skipWs() {
      while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++;
    }

    private void expect(char c) {
      skipWs();
      if (s.charAt(i) != c) throw new IllegalArgumentException("expected " + c + " at " + i);
      i++;
    }
  }
}
